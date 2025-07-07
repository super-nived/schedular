
from flask import Flask, request, jsonify,render_template
import os
import logging
from Data import ROUTING_DATA , MACHINE_TIME_FORMULA 
from flask_cors import CORS
from Pocketbase import process_all_operations,save_job_to_pb,getAndTransformJobData,getAndTransformDowntimes, getAndTransformScheduledJobs,getAllMachinesDetails
from schedule import Job, Operation, Machine, Downtime, ScheduledJob, validate_scheduling_input, choose_scheduling_approach
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('routing_debug.log'),
        logging.StreamHandler()
    ]
)

# Set to DEBUG for more verbose output
logger = logging.getLogger('routing')
# logger.setLevel(logging.DEBUG)  # Uncomment this line for very detailed logs


# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # Allows all origins (replace with specific domains if needed)
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    logger.error(f"An unhandled exception occurred: {str(e)}", exc_info=True)
    
    # Return a JSON response
    return jsonify({
        'status': 'error',
        'message': f'An unexpected error occurred: {str(e)}'
    }), 500


def evaluate_string_condition(condition, param_values):
    """Evaluate a string-based condition"""
    try:
        # Extract key elements from the condition string
        cond_str = condition.lower()
        
        # Special handling for common condition patterns
        if 'qty >= 10' in cond_str:
            return param_values['Qty'] >= 10
        elif 'fl < 1500' in cond_str:
            return param_values['FL'] < 1500
        elif 'fl < 2500' in cond_str:
            return param_values['FL'] < 2500
        elif 'fh < 1219.2' in cond_str:
            return param_values['FH'] < 1219.2
        elif 'rows <= 2' in cond_str or 'row <= 2' in cond_str:
            return param_values['Rows'] <= 2
        elif 'rows <= 3' in cond_str or 'row <= 3' in cond_str:
            return param_values['Rows'] <= 3
        elif 'l2-l1 <= 50' in cond_str:
            return param_values['L2-L1'] <= 50
        elif 'l1 = l2 = l3' in cond_str:
            return param_values['L1'] == param_values['L2'] and param_values['L2'] == param_values['L3']
        
        # For more complex conditions, we'd need to implement a more robust parser
        # This is simplified and won't handle all possible string conditions
        # print(f"Warning: Unhandled string condition: {condition}")
        return False
    except Exception as e:
        # print(f"Error evaluating string condition '{condition}': {str(e)}")
        return False

def evaluate_object_condition(condition, param_values):
    try:
        field = condition.get('field')
        op = condition.get('op')
        value = condition.get('value')
        value_field = condition.get('valueField')
        
        field_value = param_values.get(field, 0)
        compare_value = param_values.get(value_field, 0) if value_field else value
        
        # Determine if the comparison should be numerical or string-based
        is_string_comparison = isinstance(field_value, str) or isinstance(compare_value, str)
        
        if is_string_comparison:
            # Handle string comparisons (e.g., Mat == "Cu")
            field_value = str(field_value).strip()
            compare_value = str(compare_value).strip()
            # print(f"Evaluating string condition: {field} {op} '{compare_value}' (field value: '{field_value}')")
            if op == '==':
                return field_value == compare_value
            elif op == '!=':
                return field_value != compare_value
            else:
                print(f"Invalid operator for string comparison: {op}")
                return False
        else:
            # Handle numerical comparisons
            try:
                field_value = float(field_value)
                compare_value = float(compare_value)
            except (ValueError, TypeError) as e:
                print(f"Type conversion error: field_value={field_value}, compare_value={compare_value}, error={str(e)}")
                return False
            
            print(f"Evaluating numerical condition: {field} {op} {compare_value} (field value: {field_value})")
            if op == '>':
                return field_value > compare_value
            elif op == '<':
                return field_value < compare_value
            elif op == '>=':
                return field_value >= compare_value
            elif op == '<=':
                return field_value <= compare_value
            elif op == '==':
                return field_value == compare_value
            else:
                print(f"Invalid operator for numerical comparison: {op}")
                return True
                
    except Exception as e:
        print(f"Error evaluating object condition {condition}: {str(e)}")
        return False
    
def calculate_time_from_formula(formula, params):
    """
    Calculate time based on the formula string and parameters
    Returns time in MINUTES
    """
    try:
        if not formula:
            return 0
        
        # Create a safe evaluation environment with math functions
        import math
        safe_dict = {
            '__builtins__': {},
            'math': math,
            'abs': abs,
            'min': min,
            'max': max,
            'round': round,
            'pow': pow,
            # Add parameter values
            'FL': params.get('FL', 0),
            'FH': params.get('FH', 0),
            'Row': params.get('Row', 0),
            'Rows': params.get('Rows', 0),
            'Qty': params.get('Qty', 0),
            'FPI': params.get('FPI', 12),  # Default FPI value if not provided
        }
        # print(f"Calculating time for formula: {formula} with params: {params}")
        # Evaluate the formula safely (result is in hours)
        result_hours = eval(formula, safe_dict)
        # print(f"Result in hours: {result_hours}")
        # Convert hours to minutes
        result_minutes = eval(formula, safe_dict)
        # print(f"Converted result to minutes: {result_minutes}")
        
        return round(result_minutes, 4)  # Round to 4 decimal places
        
    except Exception as e:
        # print(f"Error calculating time for formula '{formula}': {str(e)}")
        return 0

def get_time_formula(machine_name, dimension, pitch):
    norm_dim = normalize_dim_pitch(dimension)
    norm_pitch = normalize_dim_pitch(pitch)
    for machine_entry in MACHINE_TIME_FORMULA:
        if machine_entry["machine"] == machine_name:
            formulas = machine_entry.get("formulas", {})

            # Find matching dimension key
            dimension_key = next((k for k in formulas if normalize_dim_pitch(k) == norm_dim), None)
            if not dimension_key:
                return False

            dimension_data = formulas[dimension_key]

            # Find matching pitch key
            pitch_key = next((k for k in dimension_data if normalize_dim_pitch(k) == norm_pitch), None)
            if not pitch_key:
                return False

            formula = dimension_data[pitch_key].get("time-formula")
            if formula:
                return formula
            else:
                False

    return False

def normalize_dim_pitch(value):
    return str(value).replace('"', '').replace('\\', '').strip()

@app.route('/occ-routes/api/calculate-routing', methods=['POST'])
def calculate_routing():
    try:
        data = request.json or {}

        # Extract input values
        sel_prod = data.get('productType', '').strip()
        material = data.get('material', '').strip()
        dim      = data.get('diameter', '').strip()
        pitch    = data.get('pitch', '').strip()
        fin_h    = float(data.get('finHeight', 0) or 0)
        fin_l    = float(data.get('finLength', 0) or 0)
        rows     = float(data.get('rows', 0) or 0)
        quantity = float(data.get('quantity', 0) or 0)
        l1       = float(data.get('l1', 0) or 0)
        l2       = float(data.get('l2', 0) or 0)
        l3       = float(data.get('l3', 0) or 0)
        fpi      = float(data.get('fpi', 17) or 17)
        job_number = int(data.get('jobNumber'))
        params = {
            'Mat': material,
            'FH': fin_h, 'FL': fin_l,
            'Rows': rows, 'Row': rows,
            'Qty': quantity, 'qty': quantity,
            'L1': l1, 'L2': l2, 'L3': l3,
            'L2-L1': l2 - l1,
            "FPI": fpi,
        }

        matched = None
        matched_key = None
        match_details = []
        matching_blocks = []  # Store all matching blocks

        # Loop over each item in the array
        for entry in ROUTING_DATA:
            for key, block in entry.items():  # each entry is like { "FCU": {...} }
                tokens = [t.strip() for t in key.split('/')]
                block_match = {
                    "product_key": key,
                    "product_match": False,
                    "dimension_match": False,
                    "pitch_match": False
                }

                if sel_prod not in tokens:
                    match_details.append(block_match)
                    continue

                block_match["product_match"] = True

                hdr = block.get('header', [])

                dim_match = any(
                    h['field'] in ('Dimension', 'Diameter') and normalize_dim_pitch(h['value']) == normalize_dim_pitch(dim)
                    for h in hdr
                )

                if not dim_match:
                    match_details.append(block_match)
                    continue

                block_match["dimension_match"] = True
                 
                # Pitch match
                pitch_match = any(
                    h['field'] == 'Pitch' and (
                        (normalize_dim_pitch(h['value']).upper() in ('NA', 'NAN') and normalize_dim_pitch(pitch).upper() in ('NA', 'NAN')) or
                        (normalize_dim_pitch(h['value']) == normalize_dim_pitch(pitch))
                    )
                    for h in hdr
                )

                if not pitch_match:
                    match_details.append(block_match)
                    continue

                block_match["pitch_match"] = True
                block_match["full_match"] = True

                # Store all matching blocks instead of breaking immediately
                matching_blocks.append({
                    'key': key,
                    'block': block,
                    'entry': entry
                })

        if not matching_blocks:
            return jsonify({
                "success": False,
                "error": "No matching routing found.",
                "match_attempts": match_details,
                "recipie":[sel_prod,dim,pitch,fin_h,fin_l,rows,quantity,l1,l2,l3,fpi] 
            })

        # NEW LOGIC: If we have multiple matches, choose based on quantity in header
        if len(matching_blocks) > 1:
            best_match = None
            best_match_key = None
            # print("Multiple matches found, evaluating quantity conditions...")
            for match_block in matching_blocks:
                print("Evaluating block:", match_block['key'])
                block = match_block['block']
                key = match_block['key']
                hdr = block.get('header', [])
                
                # Check if this block has a Qty field in header
                qty_header = None
                for h in hdr:
                    if h['field'] == 'Qty':
                        qty_header = h
                        break
                
                if qty_header:
                    print("this block has a Qty header:", qty_header)
                    # Parse the quantity condition from header
                    qty_condition = qty_header.get('value', '')
                    
                    # Handle different quantity condition formats
                    # e.g., ">=10", "<10", "10-50", etc.
                    if qty_condition.startswith('>='):
                        threshold = float(qty_condition[2:])
                        if quantity >= threshold:
                            best_match = block
                            best_match_key = key
                            break
                    elif qty_condition.startswith('<='):
                        threshold = float(qty_condition[2:])
                        if quantity <= threshold:
                            best_match = block
                            best_match_key = key
                            break
                    elif qty_condition.startswith('<'):
                        threshold = float(qty_condition[1:])
                        if quantity < threshold:
                            best_match = block
                            best_match_key = key
                            break
                    elif qty_condition.startswith('>'):
                        threshold = float(qty_condition[1:])
                        if quantity > threshold:
                            best_match = block
                            best_match_key = key
                            break
                    elif '-' in qty_condition:
                        # Handle range like "10-50"
                        min_qty, max_qty = map(float, qty_condition.split('-'))
                        if min_qty <= quantity <= max_qty:
                            best_match = block
                            best_match_key = key
                            break
                    else:
                        # Exact match
                        try:
                            if quantity == float(qty_condition):
                                best_match = block
                                best_match_key = key
                                break
                        except:
                            continue
            
            # If no quantity-based match found, use the first match
            if best_match:
                matched = best_match
                matched_key = best_match_key
            else:
                matched = matching_blocks[0]['block']
                matched_key = matching_blocks[0]['key']
        else:
            # Single match found
            matched = matching_blocks[0]['block']
            matched_key = matching_blocks[0]['key']
            print("Single match found:", matched_key)
        # Rest of your existing logic remains the same
        # Apply condition evaluation logic
        results = []
        for op_name, opts in matched.items():
            if op_name == 'header':
                continue

            chosen = None
            fallback = None

            for opt in opts:
                conds = opt.get('conditions', [])
                if not conds:
                    fallback = opt
                    continue

                ok = True
                for c in conds:
                    if isinstance(c, str):
                        ok = ok and evaluate_string_condition(c, params)
                    else:
                        ok = ok and evaluate_object_condition(c, params)

                    if not ok:
                        break

                if ok:
                    chosen = opt
                    break

            sel = chosen or fallback
            if not sel:
                continue


            machines_with_time = []
            for machine in sel['machines']:
                machine_data = machine.copy()  # Copy original machine data
                
                # Calculate time if formula exists
                formula = get_time_formula( machine_data['id'],dim, pitch)
                # print(f"Using formula for machine {machine_data['id']}: {formula}")
                if formula:
                    calculated_time = calculate_time_from_formula(formula, params)
                    machine_data['calculated_time'] = calculated_time
                    machine_data['time_unit'] = 'minutes'  # Changed from 'hours' to 'minutes'
                else:
                    machine_data['calculated_time'] = calculate_time_from_formula("(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",params)                                                               
                    machine_data['time_unit'] = 'minutes'  # Changed from 'hours' to 'minutes'
                
                machines_with_time.append(machine_data)

            results.append({
                'operation': op_name,
                'machines': machines_with_time,  # Now includes calculated times
                'sequence': sel.get('sequence', 0)
            })

        results.sort(key=lambda r: r['sequence'])
        return process_all_operations(job_number,results)
        # return jsonify(success=True, results=results,product=sel_prod, product_family=matched_key)

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500




@app.route('/occ-routes/api/calculate-routing-test', methods=['POST'])
def calculate_routing_for_test():
    try:
        data = request.json or {}

        # Extract input values
        sel_prod = data.get('productType', '').strip()
        material = data.get('material', '').strip()
        dim      = data.get('diameter', '').strip()
        pitch    = data.get('pitch', '').strip()
        fin_h    = float(data.get('finHeight', 0) or 0)
        fin_l    = float(data.get('finLength', 0) or 0)
        rows     = float(data.get('rows', 0) or 0)
        quantity = float(data.get('quantity', 0) or 0)
        l1       = float(data.get('l1', 0) or 0)
        l2       = float(data.get('l2', 0) or 0)
        l3       = float(data.get('l3', 0) or 0)
        fpi      = float(data.get('fpi', 17) or 17)
        job_number = data.get('jobNumber', '"10292637"').strip()
        params = {
            'Mat': material,
            'FH': fin_h, 'FL': fin_l,
            'Rows': rows, 'Row': rows,
            'Qty': quantity, 'qty': quantity,
            'L1': l1, 'L2': l2, 'L3': l3,
            'L2-L1': l2 - l1,
            "FPI": fpi,
        }

        matched = None
        matched_key = None
        match_details = []
        matching_blocks = []  # Store all matching blocks

        # Loop over each item in the array
        for entry in ROUTING_DATA:
            for key, block in entry.items():  # each entry is like { "FCU": {...} }
                tokens = [t.strip() for t in key.split('/')]
                block_match = {
                    "product_key": key,
                    "product_match": False,
                    "dimension_match": False,
                    "pitch_match": False
                }

                if sel_prod not in tokens:
                    match_details.append(block_match)
                    continue

                block_match["product_match"] = True

                hdr = block.get('header', [])

                dim_match = any(
                    h['field'] in ('Dimension', 'Diameter') and normalize_dim_pitch(h['value']) == normalize_dim_pitch(dim)
                    for h in hdr
                )

                if not dim_match:
                    match_details.append(block_match)
                    continue

                block_match["dimension_match"] = True
                 
                # Pitch match
                pitch_match = any(
                    h['field'] == 'Pitch' and (
                        (normalize_dim_pitch(h['value']).upper() in ('NA', 'NAN') and normalize_dim_pitch(pitch).upper() in ('NA', 'NAN')) or
                        (normalize_dim_pitch(h['value']) == normalize_dim_pitch(pitch))
                    )
                    for h in hdr
                )

                if not pitch_match:
                    match_details.append(block_match)
                    continue

                block_match["pitch_match"] = True
                block_match["full_match"] = True

                # Store all matching blocks instead of breaking immediately
                matching_blocks.append({
                    'key': key,
                    'block': block,
                    'entry': entry
                })

        if not matching_blocks:
            return jsonify({
                "success": False,
                "error": "No matching routing found.",
                "match_attempts": match_details
            })

        # NEW LOGIC: If we have multiple matches, choose based on quantity in header
        if len(matching_blocks) > 1:
            best_match = None
            best_match_key = None
            # print("Multiple matches found, evaluating quantity conditions...")
            for match_block in matching_blocks:
                print("Evaluating block:", match_block['key'])
                block = match_block['block']
                key = match_block['key']
                hdr = block.get('header', [])
                
                # Check if this block has a Qty field in header
                qty_header = None
                for h in hdr:
                    if h['field'] == 'Qty':
                        qty_header = h
                        break
                
                if qty_header:
                    print("this block has a Qty header:", qty_header)
                    # Parse the quantity condition from header
                    qty_condition = qty_header.get('value', '')
                    
                    # Handle different quantity condition formats
                    # e.g., ">=10", "<10", "10-50", etc.
                    if qty_condition.startswith('>='):
                        threshold = float(qty_condition[2:])
                        if quantity >= threshold:
                            best_match = block
                            best_match_key = key
                            break
                    elif qty_condition.startswith('<='):
                        threshold = float(qty_condition[2:])
                        if quantity <= threshold:
                            best_match = block
                            best_match_key = key
                            break
                    elif qty_condition.startswith('<'):
                        threshold = float(qty_condition[1:])
                        if quantity < threshold:
                            best_match = block
                            best_match_key = key
                            break
                    elif qty_condition.startswith('>'):
                        threshold = float(qty_condition[1:])
                        if quantity > threshold:
                            best_match = block
                            best_match_key = key
                            break
                    elif '-' in qty_condition:
                        # Handle range like "10-50"
                        min_qty, max_qty = map(float, qty_condition.split('-'))
                        if min_qty <= quantity <= max_qty:
                            best_match = block
                            best_match_key = key
                            break
                    else:
                        # Exact match
                        try:
                            if quantity == float(qty_condition):
                                best_match = block
                                best_match_key = key
                                break
                        except:
                            continue
            
            # If no quantity-based match found, use the first match
            if best_match:
                matched = best_match
                matched_key = best_match_key
            else:
                matched = matching_blocks[0]['block']
                matched_key = matching_blocks[0]['key']
        else:
            # Single match found
            matched = matching_blocks[0]['block']
            matched_key = matching_blocks[0]['key']
            print("Single match found:", matched_key)
        # Rest of your existing logic remains the same
        # Apply condition evaluation logic
        results = []
        for op_name, opts in matched.items():
            if op_name == 'header':
                continue

            chosen = None
            fallback = None

            for opt in opts:
                conds = opt.get('conditions', [])
                if not conds:
                    fallback = opt
                    continue

                ok = True
                for c in conds:
                    if isinstance(c, str):
                        ok = ok and evaluate_string_condition(c, params)
                    else:
                        ok = ok and evaluate_object_condition(c, params)

                    if not ok:
                        break

                if ok:
                    chosen = opt
                    break

            sel = chosen or fallback
            if not sel:
                continue


            machines_with_time = []
            for machine in sel['machines']:
                machine_data = machine.copy()  # Copy original machine data
                
                # Calculate time if formula exists
                formula = get_time_formula( machine_data['id'],dim, pitch)
                # print(f"Using formula for machine {machine_data['id']}: {formula}")
                if formula:
                    calculated_time = calculate_time_from_formula(formula, params)
                    machine_data['calculated_time'] = calculated_time
                    machine_data['time_unit'] = 'minutes'  # Changed from 'hours' to 'minutes'
                else:
                    machine_data['calculated_time'] = 24 * rows                                                              
                    machine_data['time_unit'] = 'minutes'  # Changed from 'hours' to 'minutes'
                
                machines_with_time.append(machine_data)

            results.append({
                'operation': op_name,
                'machines': machines_with_time,  # Now includes calculated times
                'sequence': sel.get('sequence', 0)
            })

        results.sort(key=lambda r: r['sequence'])
        return jsonify(success=True, results=results,product=sel_prod, product_family=matched_key)
        # return jsonify(success=True, results=results,product=sel_prod, product_family=matched_key)

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@app.route('/occ-routes/api/saveJob', methods=['POST'])
def save_job():
    main_data = request.get_json()
    data = main_data.get('formData', {})
    job_number = data.get('jobNumber', '10292637').strip()
    results = main_data.get('results', [])
    try:
        save_job_to_pb(data)
        return process_all_operations(job_number, results)
    except Exception as e:
        print(f"[Save Job API Error] {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/create-job-routes', methods=['GET'])
def serve_route():
    return render_template('Route.html')

#schedule apis

@app.route('/api/schedule_jobs', methods=['POST'])
def schedule_jobs():
    # Log the request
    logger.info("Received POST request for /api/schedule_jobs")
    
    # Get JSON data from request
    data = request.get_json()
    if not data:
        logger.error("No JSON data provided")
        return jsonify({
            'status': 'error',
            'message': 'No JSON data provided'
        }), 400

    # Validate input format
    if not isinstance(data, list) or not all(isinstance(item, dict) and "jobNumber" in item for item in data):
        logger.error("Invalid input format: Expected a list of objects with 'jobNumber' and optional 'priority'")
        return jsonify({
            'status': 'error',
            'message': "Invalid input format: Expected a list of objects with 'jobNumber' and optional 'priority'"
        }), 400

    # Today's date in ISO format
    today_date = datetime(2025, 7, 6).strftime("%Y-%m-%dT%H:%M:%S")

    # Step 1: Get job details
    try:
        job_details = getAndTransformJobData(data)
        if isinstance(job_details, dict) and "error" in job_details:
            logger.error(f"Failed to fetch job details: {job_details['error']}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to fetch job details: {job_details['error']}"
            }), 500
        if not job_details:
            logger.error("No job details returned")
            return jsonify({
                'status': 'error',
                'message': "No job details returned"
            }), 400
    except Exception as e:
        error_msg = f"Error in getAndTransformJobData: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 500

    # Step 2: Get downtime details (optional, default to [])
    downtime_details = []
    try:
        downtime_result = getAndTransformDowntimes(today_date)
        if isinstance(downtime_result, dict) and "error" in downtime_result:
            logger.warning(f"Failed to fetch downtime details: {downtime_result['error']}. Using empty list.")
        else:
            downtime_details = downtime_result.get("downtimes", [])
    except Exception as e:
        logger.warning(f"Error in getAndTransformDowntimes: {str(e)}. Using empty list.")

    # Step 3: Get scheduled job details (optional, default to [])
    scheduled_job_details = []
    try:
        scheduled_job_result = getAndTransformScheduledJobs(today_date)
        if isinstance(scheduled_job_result, dict) and "error" in scheduled_job_result:
            logger.warning(f"Failed to fetch scheduled job details: {scheduled_job_result['error']}. Using empty list.")
        else:
            scheduled_job_details = scheduled_job_result.get("scheduled_jobs", [])
    except Exception as e:
        logger.warning(f"Error in getAndTransformScheduledJobs: {str(e)}. Using empty list.")

    # Step 4: Get machine details
    try:
        machines_details = getAllMachinesDetails()
        if not machines_details:
            logger.error("Failed to fetch machine details: Empty or None response")
            return jsonify({
                'status': 'error',
                'message': "Failed to fetch machine details: Empty or None response"
            }), 500
    except Exception as e:
        error_msg = f"Error in getAllMachinesDetails: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 500

    # Parse machines
    machines = []
    try:
        for m in machines_details:
            machines.append(Machine(
                machine_id=m['machine_id'],
                name=m.get('name', m['machine_id']),
                machine_type=m.get('machine_type', ''),
                list_seq=m.get('list_seq', 0)
            ))
    except (KeyError, TypeError) as e:
        error_msg = f"Invalid machines data format: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 400

    # Parse downtimes
    downtimes = []
    try:
        for dt in downtime_details:
            downtimes.append(Downtime(
                machine_id=dt['machine_id'],
                start=dt['start'],
                end=dt['end'],
                reason=dt.get('reason', '')
            ))
    except (KeyError, TypeError) as e:
        error_msg = f"Invalid downtimes data format: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 400

    # Parse scheduled jobs
    scheduled_jobs = []
    try:
        for sj in scheduled_job_details:
            scheduled_jobs.append(ScheduledJob(
                job_id=sj['job_id'],
                op_id=sj['op_id'],
                machine_id=sj['machine_id'],
                start=sj['start'],
                end=sj['end']
            ))
    except (KeyError, TypeError) as e:
        error_msg = f"Invalid scheduled_jobs data format: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 400

    # Parse jobs
    jobs = []
    try:
        for input_job in job_details:
            job_id = input_job.get('job_id')
            quantity = input_job.get('quantity')
            delivery_date_str = input_job.get('delivery_date')
            priority = input_job.get('priority', 0)
            schedule_direction = input_job.get('schedule_direction', 'forward')
            operations_data = input_job.get('operations', [])

            operations = [Operation(op['op_id'], op['name'], op['possible_machines']) for op in operations_data]

            job = Job(
                job_id=job_id,
                operations=operations,
                schedule_direction=schedule_direction,
                quantity=quantity,
                delivery_date=delivery_date_str,
                priority=priority,
            )
            jobs.append(job)
    except (KeyError, TypeError) as e:
        error_msg = f"Invalid jobs data format: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 400

    # Validate scheduling input
    is_valid, warnings, recommendations = validate_scheduling_input(jobs, machines, downtimes, scheduled_jobs)

    if not is_valid:
        logger.error("Input validation failed")
        return jsonify({
            'status': 'error',
            'message': 'Input validation failed',
            'warnings': warnings,
            'recommendations': recommendations
        }), 400

    print("\n" + "="*60)
    print("STARTING MIXED SCHEDULING")
    print("="*60)

    try:
        result = choose_scheduling_approach(jobs, machines, downtimes, scheduled_jobs)
        
        # Extract the schedule_result from the 'mixed' approach
        schedule_result = result.get('mixed', {}).get('schedule_result', {})
        
        return jsonify(schedule_result), 200

    except Exception as e:
        # Log the exception and return a JSON error response
        error_msg = f"An unexpected error occurred during scheduling: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
