import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from datetime import datetime,timedelta
import random
import logging
from logging.handlers import RotatingFileHandler
import time
# Load environment variables
load_dotenv()

PB_BASE_URL = os.getenv("PB_BASE_URL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
PLANT_CODE = os.getenv("PLANT_CODE", "")
# Initialize Flask appP

# Setup log directory and file
LOG_DIR = "logs"
LOG_FILE = "api_activity.log"
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, LOG_FILE)

log_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

logger = logging.getLogger("API_Logger")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# New function to log detailed error messages for failed sections
def log_detailed_error(section, error_message, details=None):
    error_msg = f"[Failed Section: {section}] {error_message}"
    if details:
        error_msg += f" | Details: {details}"
    logger.error(error_msg)
    return error_msg

def login_admin():
    url = f"{PB_BASE_URL}/api/admins/auth-with-password"
    data = {
        "identity": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json().get("token")
    except requests.RequestException as e:
        error_details = f"Failed to authenticate admin with email {ADMIN_EMAIL}. Error: {str(e)}"
        log_detailed_error("Admin Login", "Authentication failed", error_details)
        logger.error(f"[Login Error] {e}")
        return None

def get_filtered_records(collection_name, auth_token, filter_query="", page=1, per_page=500):
    url = f"{PB_BASE_URL}/api/collections/{collection_name}/records"
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    params = {
        "page": page,
        "perPage": per_page
    }
    if filter_query:
        params["filter"] = filter_query
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.RequestException as e:
        error_details = f"Failed to fetch records from collection {collection_name} with filter '{filter_query}'. Error: {str(e)}"
        log_detailed_error("Fetch Records", "Record retrieval failed", error_details)
        logger.error(f"[Fetch Error] {e}")
        return []

def get_job_details_id(auth_token, job_number):
    collection_name = f"{PLANT_CODE}_jobDetails"
    filter_query = f'jobNumber = "{job_number}"'
    records = get_filtered_records(collection_name, auth_token, filter_query)
    if records:
        return records[0].get("id")
    else:
        error_details = f"No job details found for jobNumber {job_number}"
        log_detailed_error("Job Details Lookup", "Job not found", error_details)
        logger.warning(f"❌ No record found for jobNumber: {job_number}")
        return None

def get_recipe_route_id(auth_token, job_id, operation_name):
    collection_name = f"{PLANT_CODE}_jobProductReceipeRoutes"
    filter_query = f'jobId = "{job_id}" && operationName = "{operation_name}"'
    records = get_filtered_records(collection_name, auth_token, filter_query)
    if records:
        return records[0].get("id")
    else:
        error_details = f"No recipe route found for jobId {job_id} and operationName {operation_name}"
        log_detailed_error("Recipe Route Lookup", "Recipe route not found", error_details)
        logger.warning(f"❌ No record found for jobId: {job_id} and operationName: {operation_name}")
        return None

def get_machine_id(token, machine_code):
    url = f"{PB_BASE_URL}/api/collections/{PLANT_CODE}_machineMaster/records"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "page": 1,
        "perPage": 1,
        "filter": f'machineId = "{machine_code}"',
        "fields": "id"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])
        if items:
            return items[0]["id"]
        else:
            error_details = f"No machine found with machineId {machine_code}"
            log_detailed_error("Machine Lookup", "Machine not found", error_details)
            logger.warning(f"[Machine Not Found] No machine with machineId '{machine_code}'")
            return None
    except requests.RequestException as e:
        error_details = f"Failed to fetch machine with machineId {machine_code}. Error: {str(e)}"
        log_detailed_error("Machine Lookup", "Machine retrieval failed", error_details)
        logger.error(f"[Get Machine Error] {e}")
        return None

def get_machine_name_by_id(token, id):
    url = f"{PB_BASE_URL}/api/collections/{PLANT_CODE}_machineMaster/records"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "page": 1,
        "perPage": 1,
        "filter": f'id = "{id}"',
        "fields": "machineId"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])
        if items:
            return items[0]["machineId"]
        else:
            error_details = f"No machine found with machineId {id}"
            log_detailed_error("Machine Lookup", "Machine not found", error_details)
            logger.warning(f"[Machine Not Found] No machine with machineId '{id}'")
            return None
    except requests.RequestException as e:
        error_details = f"Failed to fetch machine with machineId {id}. Error: {str(e)}"
        log_detailed_error("Machine Lookup", "Machine retrieval failed", error_details)
        logger.error(f"[Get Machine Error] {e}")
        return None 


def save_product_recipe(token, job_id, payload):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    collection_url = f"{PB_BASE_URL}/api/collections/{PLANT_CODE}_jobProductReceipeRoutes/records"
    payload["jobId"] = job_id

    try:
        response = requests.post(collection_url, json=payload, headers=headers)
        response.raise_for_status()
        created_record = response.json()
        record_id = created_record.get('id')
        logger.info(f"✅ Saved operation: {payload['operationName']} (Seq: {payload['sequence']}) with ID: {record_id}")
        return record_id
    except requests.RequestException as e:
        error_details = f"Failed to save product recipe for jobId {job_id}, operation {payload.get('operationName', 'unknown')}. Error: {str(e)}"
        log_detailed_error("Save Product Recipe", "Failed to save recipe", error_details)
        logger.error(f"❌ Failed to save operation '{payload['operationName']}' for jobId '{job_id}': {e}")
        return None

def save_recipe_route_machine(token, recipe_route_id , machine_code, cycle_time):
    machine_id = get_machine_id(token, machine_code)

    if not recipe_route_id:
        error_details = f"Recipe route ID missing for machine {machine_code}"
        log_detailed_error("Save Recipe Route Machine", "Missing recipe route ID", error_details)
        logger.warning(f"⚠️ Recipe route ID missing for machine '{machine_code}'")
        return
    if not machine_id:
        error_details = f"Machine ID not found for machineCode {machine_code}"
        log_detailed_error("Save Recipe Route Machine", "Missing machine ID", error_details)
        logger.warning(f"⚠️ Machine ID not found for '{machine_code}'")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    collection_url = f"{PB_BASE_URL}/api/collections/{PLANT_CODE}_receipeRouteMachines/records"
    payload = {
        "jobreceipeId": recipe_route_id,
        "machine": machine_id,
        "machineId": machine_code,
        "cycleTime": cycle_time
    }

    try:
        response = requests.post(collection_url, json=payload, headers=headers)
        response.raise_for_status()
        created_record = response.json()
        record_id = created_record.get('id')
        logger.info(f"✅ Machine '{machine_code}' saved with ID {record_id}")
    except requests.RequestException as e:
        error_details = f"Failed to save machine {machine_code} for recipe route {recipe_route_id}. Error: {str(e)}"
        log_detailed_error("Save Recipe Route Machine", "Failed to save machine", error_details)
        logger.error(f"❌ Failed to save machine '{machine_code}': {e}")

def is_job_id_exist_in_product_recipe(token, job_id):
    collection_name = f"{PLANT_CODE}_jobProductReceipeRoutes"
    filter_query = f'jobId = "{job_id}"'
    records = get_filtered_records(collection_name, token, filter_query, page=1, per_page=1)
    return bool(records)

def process_all_operations(job_number, results):
    logger.info(f"🏭 🔨 🏗️ ⚙️ 🔧 🚧 🛠️ 📋 🔄 🎯 Trying to save all operations for job == {job_number}")
    try:
        token = login_admin()
        if token:
            job_details_id = get_job_details_id(token, job_number)
            if not job_details_id:
                error_details = f"Job details not found for jobNumber {job_number}"
                log_detailed_error("Process Operations", "Job details lookup failed", error_details)
                logger.warning(f"❌ Job details not found for jobNumber: {job_number}")
                return jsonify(success=False, error="Job details not found"), 404

            is_job_id_exist = is_job_id_exist_in_product_recipe(token, job_details_id)
            if not is_job_id_exist:
                all_success = True
                total_ops = len(results)
                for i, operation_data in enumerate(results):
                    operation_name = operation_data.get("operation", "unknown")
                    previous_sequence = results[i - 1]["sequence"] if i > 0 else None
                    next_sequence = results[i + 1]["sequence"] if i < total_ops - 1 else None

                    operation_data["previousSequence"] = previous_sequence
                    operation_data["nextSequence"] = next_sequence

                    logger.info(f"🛠️ Saving operation '{operation_name}' (sequence: {operation_data.get('sequence')})")
                    res = save_data_to_pocketbase(job_details_id, operation_data)

                    if isinstance(res, tuple) and res[1] == 200:
                        logger.info(f"✅ Operation '{operation_name}' saved successfully")
                    else:
                        error_details = f"Failed to save operation {operation_name} for job {job_number}"
                        log_detailed_error("Process Operations", "Operation save failed", error_details)
                        logger.error(f"❌ Failed to save operation '{operation_name}'")
                        all_success = False

                if all_success:
                    logger.info(f"🎉 🏭 🔨 🏗️ ⚙️ 🔧 🚧 🛠️ 📋 🔄 🎯 All operations and machines saved successfully for job == {job_number}")
                else:
                    error_details = f"Some operations or machines failed to save for job {job_number}"
                    log_detailed_error("Process Operations", "Partial failure in saving operations", error_details)
                    logger.warning(f"⚠️ Some operations or machines failed for job == {job_number}")
                return jsonify({"success": True, "message": "Operations processed successfully", "matches": results}), 200
            else:
                error_details = f"Job ID {job_details_id} already exists in product recipe"
                log_detailed_error("Process Operations", "Job ID already exists", error_details)
                logger.warning(f"❌ Job ID {job_details_id} already exists in product recipe. Skipping operations.")
                return jsonify(success=False, message="Job ID already exists, operations skipped"), 500
        else:
            error_details = "Admin login failed, unable to process operations"
            log_detailed_error("Process Operations", "Admin login failure", error_details)
            logger.error("❌ Failed to login as admin. Cannot process operations.")
            return jsonify(success=False, error="Failed to login as admin"), 500
    except Exception as e:
        error_details = f"Unexpected error while processing operations for job {job_number}. Error: {str(e)}"
        log_detailed_error("Process Operations", "Unexpected error", error_details)
        logger.error(f"❌ Error processing operations: {str(e)}")
        return jsonify(success=False, error=str(e)), 500

def save_data_to_pocketbase(job_details_id, response_data):
    try:
        token = login_admin()
        if token:
            logger.info(f"➡️ Trying to save operation '{response_data.get('operation', 'unknown')}' to job '{job_details_id}'")
            product_recipe_id = save_product_recipe(token, job_details_id, {
                "operationName": response_data.get("operation", "no operation"),
                "erpOperationSequence": response_data.get("operation", "no operation"),
                "sequence": response_data.get("sequence", 10),
                "nextSequence": response_data.get("nextSequence"),
                "previousSequence": response_data.get("previousSequence")
            })

            if not product_recipe_id:
                error_details = f"Failed to save product recipe for jobId {job_details_id}, operation {response_data.get('operation', 'unknown')}"
                log_detailed_error("Save Data to PocketBase", "Product recipe save failed", error_details)
                logger.error(f"❌ Product recipe was not saved for jobId '{job_details_id}', operation skipped.")
                return jsonify(success=False, error="Failed to save product recipe"), 500

            for machine in response_data.get("machines", []):
                machine_code = machine.get("id")
                cycle_time = machine.get("calculated_time", "0")
                logger.info(f"⚙️ Trying to save machine '{machine_code}' for operation '{response_data.get('operation', 'unknown')}'")
                save_recipe_route_machine(token, recipe_route_id=product_recipe_id, machine_code=machine_code, cycle_time=cycle_time)

            logger.info(f"✅ Product Recipe ID: {product_recipe_id}")
            return jsonify(success=True, message="Data saved successfully"), 200
        else:
            error_details = "Admin login failed, unable to save data to PocketBase"
            log_detailed_error("Save Data to PocketBase", "Admin login failure", error_details)
            logger.error("❌ Failed to login as admin. Cannot save data to PocketBase.")
            return jsonify(success=False, error="Failed to login as admin"), 500
    except Exception as e:
        error_details = f"Unexpected error while saving data for jobId {job_details_id}, operation {response_data.get('operation', 'unknown')}. Error: {str(e)}"
        log_detailed_error("Save Data to PocketBase", "Unexpected error", error_details)
        logger.error(f"❌ Error saving data to PocketBase: {str(e)}")
        return jsonify(success=False, error=str(e)), 500
    

def save_job_to_pb(data):
    if not data:
        return jsonify({
            "success": False,
            "error": "No data provided"
        }), 400

    # Get admin token
    token = login_admin()
    if not token:
        return jsonify({
            "success": False,
            "error": "Failed to authenticate with PocketBase"
        }), 500

    try:
        # Extract input values
        sel_prod   = data.get('productType', '').strip()
        material   = data.get('material', '').strip()
        dim        = data.get('diameter', '').strip()
        pitch      = data.get('pitch', '').strip()
        fin_h      = float(data.get('finHeight', 0) or 0)
        fin_l      = float(data.get('finLength', 0) or 0)
        rows       = float(data.get('rows', 0) or 0)
        quantity   = float(data.get('quantity', 0) or 0)
        l1         = float(data.get('l1', 0) or 0)
        l2         = float(data.get('l2', 0) or 0)
        l3         = float(data.get('l3', 0) or 0)
        fpi        = float(data.get('fpi', 17) or 17)
        job_number = data.get('jobNumber', '').strip()
        # so_line_number = data.get('soLineNumber', '12345').strip()
        # so_number = data.get('soNumber', '').strip()
        # Generate random job number if not provided
        if not job_number:
            job_number = f"{random.randint(10000000, 99999999)}"

        # Prepare data for PocketBase (mapping frontend fields to database schema)
        pb_data = {
            "jobNumber": job_number,
            "jobQty": int(quantity) if quantity else None,
            "jobCreationDate": datetime.now().isoformat(),
            "jobStatus": "Created",
            "lastUpdateDate": datetime.now().isoformat(),

            "productType": sel_prod,

            "fPI": str(fpi),
            "dia": dim,
            "pitch": pitch,
            "length": str(fin_l) if fin_l else "",
            "row": str(rows) if rows else "",
            "height": str(fin_h) if fin_h else "",
            "qnty": str(quantity) if quantity else "",

            "L1": str(l1) if l1 else "",
            "L2": str(l2) if l2 else "",
            "L3": str(l3) if l3 else "",
            # "soLineNumber": so_line_number,
            # "soNumber": so_number,
            "customerApproved": "No"
        }

        # Remove None values
        pb_data = {k: v for k, v in pb_data.items() if v is not None}

        # Make request to PocketBase
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = f"{PB_BASE_URL}/api/collections/{PLANT_CODE}_jobDetails/records"
        response = requests.post(url, json=pb_data, headers=headers)

        if response.status_code in [200, 201]:
            pb_response = response.json()
            return jsonify({
                "success": True,
                "message": "Job saved successfully",
                "data": {
                    "id": pb_response.get("id"),
                    "jobNumber": pb_response.get("jobNumber"),
                    "created": pb_response.get("created")
                }
            }), 200
        else:
            error_data = response.json() if response.content else {}
            return jsonify({
                "success": False,
                "error": f"PocketBase error: {response.status_code}",
                "details": error_data
            }), response.status_code

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Invalid data format: {str(e)}"
        }), 400

    except Exception as e:
        print(f"[Save Job Error] {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500
    








#scheduler pocketbase logic

def format_iso(dt_str):
    try:
        return datetime.fromisoformat(dt_str).strftime('%Y-%m-%dT%H:%M:%S')
    except Exception:
        return dt_str or ""

def getJobDetailsFromJobNumbers(auth_token, job_numbers):
    """
    Fetch raw job details and machine records for multiple job numbers - optimized
    
    Args:
        auth_token: Authentication token for PocketBase
        job_numbers: List of job numbers or single job number (string/list)
    
    Returns:
        List of raw records from PocketBase
    """
    start_time = time.time()
    
    collection_name = f"{PLANT_CODE}_receipeRouteMachines"
    url = f"{PB_BASE_URL}/api/collections/{collection_name}/records"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Handle input normalization
    if isinstance(job_numbers, str):
        job_numbers = [job_numbers]
    elif not isinstance(job_numbers, list):
        job_numbers = list(job_numbers)

    # Create filter query
    if len(job_numbers) == 1:
        filter_query = f"jobreceipeId.jobId.jobNumber='{job_numbers[0]}'"
    else:
        job_filters = [f"jobreceipeId.jobId.jobNumber='{job_num}'" for job_num in job_numbers]
        filter_query = f"({' || '.join(job_filters)})"

    # Optimized parameters - larger page size, timeout
    params = {
        "page": 1,
        "perPage": 500,  # Increased from 40 to reduce requests
        "filter": filter_query,
        "expand": "jobreceipeId,jobreceipeId.jobId,machine",
        "sort": "-created"
    }

    all_records = []
    page = 1

    try:
        while True:
            params["page"] = page
            
            # Track individual request time
            request_start = time.time()
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            request_time = time.time() - request_start
            
            data = response.json()
            records = data.get("items", [])
            all_records.extend(records)
            
            print(f"[DB Request] Page {page}: {len(records)} records fetched in {request_time:.3f}s")

            # Break if no more records or reached last page
            if not records or len(records) < params["perPage"] or page >= data.get("totalPages", 1):
                break

            page += 1

    except requests.RequestException as e:
        fetch_time = time.time() - start_time
        error_details = f"Failed to fetch machine records for job numbers {job_numbers}. Error: {str(e)}"
        log_detailed_error("Fetch Machine Records", "Retrieval failed", error_details)
        logger.error(f"[Fetch Machine Records Error] {e} (Time: {fetch_time:.3f}s)")
        print(f"[DB Fetch Error] Total time before error: {fetch_time:.3f}s")
        return None

    fetch_time = time.time() - start_time
    logger.info(f"[DB Fetch Time] Retrieved {len(all_records)} records for {len(job_numbers)} job(s) in {fetch_time:.3f}s")
    print(f"[DB Fetch Complete] Total time: {fetch_time:.3f}s | Records: {len(all_records)} | Job Numbers: {job_numbers}")

    if not all_records:
        error_details = f"No machine records found for job numbers {job_numbers}"
        log_detailed_error("Fetch Machine Records", "No records found", error_details)
        print(f"[DB Fetch Warning] No records found in {fetch_time:.3f}s")
        return None

    return all_records

def transformJobData(raw_records, requested_job_data):
    """
    Transform raw PocketBase records into structured job data - optimized
    
    Args:
        raw_records: List of raw records from PocketBase
        requested_job_data: List of job data with job numbers and priorities 
                           Format: [{"jobNumber": "123", "priority": 1}, ...]
                           OR List of job numbers (for backward compatibility)
    
    Returns:
        Dictionary with job numbers as keys and transformed job data as values
    """
    start_time = time.time()
    
    if not raw_records:
        return {}

    # Handle input format - support both new and old formats
    job_priority_map = {}
    requested_job_numbers = []
    
    if isinstance(requested_job_data, str):
        # Single job number string
        requested_job_numbers = [requested_job_data]
        job_priority_map[requested_job_data] = 0
    elif isinstance(requested_job_data, list):
        if requested_job_data and isinstance(requested_job_data[0], dict):
            # New format: [{"jobNumber": "123", "priority": 1}, ...]
            for job_data in requested_job_data:
                job_number = job_data.get("jobNumber", "")
                priority = job_data.get("priority", 0)
                if job_number:
                    requested_job_numbers.append(job_number)
                    job_priority_map[job_number] = priority
        else:
            # Old format: ["123", "456", ...]
            for job_number in requested_job_data:
                requested_job_numbers.append(job_number)
                job_priority_map[job_number] = 0
    else:
        # Other iterable types
        for job_number in requested_job_data:
            requested_job_numbers.append(job_number)
            job_priority_map[job_number] = 0

    # Process all records and group by job number - optimized structure
    job_data = {}
    
    for record in raw_records:
        expand_data = record.get("expand", {})
        jobreceipe = expand_data.get("jobreceipeId", {})
        job_details = jobreceipe.get("expand", {}).get("jobId", {})
        
        if not job_details or not jobreceipe:
            continue

        job_number = job_details.get("jobNumber")
        if not job_number:
            continue
            
        # Initialize job data structure once
        if job_number not in job_data:
            job_data[job_number] = {
                "jobDetails": job_details,
                "operations": {}
            }

        operation_name = jobreceipe.get("operationName", "unknown")
        
        # Initialize operation once
        if operation_name not in job_data[job_number]["operations"]:
            job_data[job_number]["operations"][operation_name] = {
                "operationDetails": jobreceipe,
                "machines": []
            }

        # Process machine data
        machine_id = record.get("machineId", "unknown")
        cycle_time_str = record.get("cycleTime", 24)
        
        # Optimized type conversion
        try:
            cycle_time = round(float(cycle_time_str)) if cycle_time_str else 0
        except (ValueError, TypeError):
            cycle_time = 0
        
        job_data[job_number]["operations"][operation_name]["machines"].append(
            (machine_id, cycle_time)
        )

    # Transform to final format
    result = {}
    schedule_start = datetime(2025, 6, 12, 0, 0, 0)
    delivery_date = schedule_start + timedelta(days=30)
    delivery_date_str = delivery_date.strftime("%Y-%m-%dT%H:%M:%S")
    
    for job_number in requested_job_numbers:
        if job_number not in job_data:
            error_details = f"No job data found for jobNumber '{job_number}'"
            log_detailed_error("Transform Job Data", "No job data", error_details)
            result[job_number] = None
            continue

        job_info = job_data[job_number]
        job_details = job_info["jobDetails"]

        # Build operations list
        operations = []
        for op_name, op_data in job_info["operations"].items():
            operation = {
                "op_id": op_data["operationDetails"]["id"],
                "name": op_name,
                "possible_machines": op_data["machines"]
            }
            operations.append(operation)

        # Sort operations by sequence
        operations.sort(key=lambda op: int(job_info["operations"][op["name"]]["operationDetails"].get("sequence", "0")) 
                       if job_info["operations"][op["name"]]["operationDetails"].get("sequence", "0").isdigit() else 0)

        # Build final job dictionary with mapped priority
        job_dict = {
            "job_id": int(job_details.get("jobNumber", 0)),
            "quantity": int(job_details.get("jobQty", 0)) or 0,
            "delivery_date": delivery_date_str,
            "priority": job_priority_map.get(job_number, 0),  # Use mapped priority
            "schedule_direction": "forward",
            "operations": operations
        }

        result[job_number] = job_dict

    transform_time = time.time() - start_time
    print(f"[Transform Time] Processed {len(requested_job_numbers)} job(s) in {transform_time:.3f}s")
    
    return result

def getAndTransformJobData(job_data):
    """
    Main function that handles authentication, fetching, and transforming job data
    
    Args:
        job_data: List of job data with job numbers and priorities
                 Format: [{"jobNumber": "123", "priority": 1}, ...]
                 OR List of job numbers (for backward compatibility): ["123", "456", ...]
                 OR Single job number string: "123"
    
    Returns:
        List of job dictionaries or error dictionary
    """
    total_start_time = time.time()
    
    # Step 1: Authenticate
    auth_token = login_admin()
    print("llllllllllllllllllll",auth_token)
    if not auth_token:
        logger.error("[Main Error] Failed to authenticate with Pocketbase")
        return {"error": "Failed to authenticate with Pocketbase"}
    
    # Extract job numbers for database fetch
    if isinstance(job_data, str):
        job_numbers = [job_data]
    elif isinstance(job_data, list):
        if job_data and isinstance(job_data[0], dict):
            # New format: extract job numbers from dictionaries
            job_numbers = [item.get("jobNumber", "") for item in job_data if item.get("jobNumber")]
        else:
            # Old format: list of job numbers
            job_numbers = job_data
    else:
        job_numbers = list(job_data)
    
    # Step 2: Get raw job details
    raw_records = getJobDetailsFromJobNumbers(auth_token, job_numbers)
    fetch_time = time.time() - total_start_time
    print(f"After fetching raw data: {fetch_time:.3f}s")
    
    if raw_records is None:
        print(f"Failed to fetch data in {fetch_time:.3f}s")
        logger.error("[Main Error] Failed to fetch job data")
        return {"error": "Failed to fetch job data"}
    
    # Step 3: Transform the raw data
    transform_start = time.time()
    job_data_dict = transformJobData(raw_records, job_data)  # Pass original job_data
    transform_time = time.time() - transform_start
    print(f"After transforming data: {transform_time:.3f}s")
    
    # Step 4: Convert to list format
    jobs = []
    job_numbers_list = [job_data] if isinstance(job_data, str) else job_numbers
    
    for job_number in job_numbers_list:
        job = job_data_dict.get(job_number)
        if job is None:
            logger.warning(f"[Main Warning] No job found for jobNumber '{job_number}'")
            continue
        jobs.append(job)
    
    total_time = time.time() - total_start_time
    print(f"[Total Process Time] Complete process took {total_time:.3f}s")
    
    return jobs


def getScheduledJobDetails(auth_token, stop_time_after):
    """
    Fetch raw scheduled job details from OCCUAT_schedule filtered by scheduleStopTime.
    
    Args:
        auth_token: Authentication token for PocketBase
        stop_time_after: Datetime string (ISO format) to filter scheduleStopTime (e.g., "2025-06-12T00:00:00")
    
    Returns:
        List of raw records from PocketBase or None if failed
    """
    start_time = time.time()
    
    collection_name = f"{PLANT_CODE}_schedule"
    url = f"{PB_BASE_URL}/api/collections/{collection_name}/records"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    filter_query = f"scheduleStopTime>'{stop_time_after}'"
    
    params = {
        "page": 1,
        "perPage": 500,
        "filter": filter_query,
        "expand": "jobId",
        "sort": "scheduleStartTime"
    }
    
    all_records = []
    page = 1
    
    try:
        while True:
            params["page"] = page
            request_start = time.time()
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            request_time = time.time() - request_start
            
            data = response.json()
            records = data.get("items", [])
            all_records.extend(records)
            
            logger.info(f"[Scheduled Jobs Request] Page {page}: {len(records)} records fetched in {request_time:.3f}s")
            print(f"[DB Request] Page {page}: {len(records)} records fetched in {request_time:.3f}s")
            
            if not records or len(records) < params["perPage"] or page >= data.get("totalPages", 1):
                break
                
            page += 1
    
    except requests.RequestException as e:
        fetch_time = time.time() - start_time
        error_details = f"Failed to fetch scheduled jobs after {stop_time_after}. Error: {str(e)}"
        log_detailed_error("Fetch Scheduled Jobs", "Retrieval failed", error_details)
        logger.error(f"[Fetch Scheduled Jobs Error] {e} (Time: {fetch_time:.3f}s)")
        print(f"[DB Fetch Error] Total time before error: {fetch_time:.3f}s")
        return None
    
    fetch_time = time.time() - start_time
    logger.info(f"[DB Fetch Time] Retrieved {len(all_records)} scheduled job records after {stop_time_after} in {fetch_time:.3f}s")
    print(f"[DB Fetch Complete] Total time: {fetch_time:.3f}s | Records: {len(all_records)}")
    
    if not all_records:
        error_details = f"No scheduled job records found after {stop_time_after}"
        log_detailed_error("Fetch Scheduled Jobs", "No records found", error_details)
        print(f"[DB Fetch Warning] No records found in {fetch_time:.3f}s")
        return None
    
    return all_records

def transformScheduledJobData(raw_records):
    """
    Transform raw OCCUAT_schedule records into structured scheduled job data.
    
    Args:
        raw_records: List of raw records from PocketBase
    
    Returns:
        Dictionary with 'scheduled_jobs' key containing a list of transformed job schedules
    """
    start_time = time.time()
    
    if not raw_records:
        return {"scheduled_jobs": []}
    
    scheduled_jobs = []
    
    for record in raw_records:
        expand_data = record.get("expand", {})
        job_details = expand_data.get("jobId", {})
        
        job_number = job_details.get("jobNumber")
        if not job_number:
            logger.warning(f"[Transform Warning] Skipping record with missing jobNumber: {record.get('id')}")
            continue
        
        try:
            job_id = int(job_number)
        except (ValueError, TypeError):
            logger.warning(f"[Transform Warning] Invalid jobNumber '{job_number}' in record {record.get('id')}")
            continue
        
        sequence = record.get("sequence", "0")
        try:
            op_id = int(sequence) if sequence.isdigit() else 0
        except (ValueError, TypeError):
            op_id = 0
        
        scheduled_job = {
            "job_id": job_id,
            "op_id": op_id,
            "machine_id": record.get("machineId", "unknown"),
            "start": format_iso(record.get("scheduleStartTime", "")),
            "end": format_iso(record.get("scheduleStopTime", ""))
        }
        
        if not scheduled_job["start"] or not scheduled_job["end"]:
            logger.warning(f"[Transform Warning] Missing start/end time in record {record.get('id')}")
            continue
            
        scheduled_jobs.append(scheduled_job)
    
    transform_time = time.time() - start_time
    logger.info(f"[Transform Time] Processed {len(scheduled_jobs)} scheduled job(s) in {transform_time:.3f}s")
    print(f"[Transform Time] Processed {len(scheduled_jobs)} job(s) in {transform_time:.3f}s")
    
    return {"scheduled_jobs": scheduled_jobs}

def getAndTransformScheduledJobs(stop_time_after):

    """
    Main function to authenticate, fetch, and transform scheduled job data after a given stop time.
    
    Args:
        stop_time_after: Datetime string (ISO format) to filter scheduleStopTime (e.g., "2025-06-12T00:00:00")
    
    Returns:
        Dictionary with 'scheduled_jobs' key or error dictionary
    """
    total_start_time = time.time()
    
    # Step 1: Authenticate
    auth_token = login_admin()
    if not auth_token:
        logger.error("[Main Error] Failed to authenticate with Pocketbase")
        return {"error": "Failed to authenticate with Pocketbase"}
    
    # Step 2: Get raw scheduled job details
    raw_records = getScheduledJobDetails(auth_token, stop_time_after)
    fetch_time = time.time() - total_start_time
    print(f"After fetching raw data: {fetch_time:.3f}s")
    
    if raw_records is None:
        logger.error("[Main Error] Failed to fetch scheduled job data")
        return {"error": "Failed to fetch scheduled job data"}
    
    # Step 3: Transform the raw data
    transform_start = time.time()
    result = transformScheduledJobData(raw_records)
    transform_time = time.time() - transform_start
    print(f"After transforming data: {transform_time:.3f}s")
    
    total_time = time.time() - total_start_time
    logger.info(f"[Total Process Time] Complete scheduled jobs process took {total_time:.3f}s")
    print(f"[Total Process Time] Complete process took {total_time:.3f}s")
    
    return result


def getDowntimeDetails(auth_token, start_date_after):
    """
    Fetch raw downtime records from OCCUAT_shift_downtime filtered by start_date.
    
    Args:
        auth_token: Authentication token for PocketBase
        start_date_after: Datetime string (ISO format) to filter start_date (e.g., "2025-06-12T00:00:00")
    
    Returns:
        List of raw records from PocketBase or None if failed
    """
    start_time = time.time()
    
    collection_name = f"{PLANT_CODE}_shift_downtime"
    url = f"{PB_BASE_URL}/api/collections/{collection_name}/records"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    filter_query = f"end_date>'{start_date_after}'"
    
    params = {
        "page": 1,
        "perPage": 500,
        "filter": filter_query,
        "expand": "machines",
        "sort": "start_date"
    }
    
    all_records = []
    page = 1
    
    try:
        while True:
            params["page"] = page
            request_start = time.time()
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            request_time = time.time() - request_start
            
            data = response.json()
            records = data.get("items", [])
            all_records.extend(records)
            
            logger.info(f"[Downtime Request] Page {page}: {len(records)} records fetched in {request_time:.3f}s")
            print(f"[DB Request] Page {page}: {len(records)} records fetched in {request_time:.3f}s")
            
            if not records or len(records) < params["perPage"] or page >= data.get("totalPages", 1):
                break
                
            page += 1
    
    except requests.RequestException as e:
        fetch_time = time.time() - start_time
        error_details = f"Failed to fetch downtime records after {start_date_after}. Error: {str(e)}"
        log_detailed_error("Fetch Downtime Records", "Retrieval failed", error_details)
        logger.error(f"[Fetch Downtime Error] {e} (Time: {fetch_time:.3f}s)")
        print(f"[DB Fetch Error] Total time before error: {fetch_time:.3f}s")
        return None
    
    fetch_time = time.time() - start_time
    logger.info(f"[DB Fetch Time] Retrieved {len(all_records)} downtime records after {start_date_after} in {fetch_time:.3f}s")
    print(f"[DB Fetch Complete] Total time: {fetch_time:.3f}s | Records: {len(all_records)}")
    
    if not all_records:
        error_details = f"No downtime records found after {start_date_after}"
        log_detailed_error("Fetch Downtime Records", "No records found", error_details)
        print(f"[DB Fetch Warning] No records found in {fetch_time:.3f}s")
        return None
    
    return all_records

def transformDowntimeData(auth_token,raw_records):
    """
    Transform raw OCCUAT_shift_downtime records into structured downtime data.
    
    Args:
        raw_records: List of raw records from PocketBase
    
    Returns:
        Dictionary with 'downtimes' key containing a list of transformed downtime records
    """
    start_time = time.time()
    
    if not raw_records:
        return {"downtimes": []}
    
    downtimes = []
    
    for record in raw_records:
        expand_data = record.get("expand", {})
        machines = expand_data.get("machines", [])
        
        # Handle multiple machines (since machines is a relation with maxSelect: null)
        machine_ids = machines if isinstance(machines, list) else [machines] if machines else []
        if not machine_ids:
            logger.warning(f"[Transform Warning] Skipping record with missing machines: {record.get('id')}")
            continue
        
        for machine in machine_ids:
            machine_id = machine.get("id") if isinstance(machine, dict) else machine
            
            downtime = {
                "machine_id": get_machine_name_by_id(auth_token,machine_id),
                "start": format_iso(record.get("start_date", "")),
                "end": format_iso(record.get("end_date", "")),
                "reason": record.get("reason_code", "unknown")
            }
            
            if not downtime["start"]:
                logger.warning(f"[Transform Warning] Missing start_date in record {record.get('id')}")
                continue
                
            # end_date is optional, so only warn if start_date exists but end_date is missing
            if not downtime["end"] and downtime["start"]:
                logger.warning(f"[Transform Warning] Missing end_date in record {record.get('id')}")
            
            downtimes.append(downtime)
    
    transform_time = time.time() - start_time
    logger.info(f"[Transform Time] Processed {len(downtimes)} downtime(s) in {transform_time:.3f}s")
    print(f"[Transform Time] Processed {len(downtimes)} downtime(s) in {transform_time:.3f}s")
    
    return {"downtimes": downtimes}

def getAndTransformDowntimes(start_date_after):
    """
    Main function to authenticate, fetch, and transform downtime data after a given start date.
    
    Args:
        start_date_after: Datetime string (ISO format) to filter start_date (e.g., "2025-06-12T00:00:00")
    
    Returns:
        Dictionary with 'downtimes' key or error dictionary
    """
    total_start_time = time.time()
    
    # Step 1: Authenticate
    auth_token = login_admin()
    if not auth_token:
        logger.error("[Main Error] Failed to authenticate with Pocketbase")
        return {"error": "Failed to authenticate with Pocketbase"}
    
    # Step 2: Get raw downtime details
    raw_records = getDowntimeDetails(auth_token, start_date_after)
    fetch_time = time.time() - total_start_time
    print(f"After fetching raw data: {fetch_time:.3f}s")
    
    if raw_records is None:
        logger.error("[Main Error] Failed to fetch downtime data")
        return {"error": "Failed to fetch downtime data"}
    
    # Step 3: Transform the raw data
    transform_start = time.time()
    result = transformDowntimeData(auth_token,raw_records)
    transform_time = time.time() - transform_start
    print(f"After transforming data: {transform_time:.3f}s")
    
    total_time = time.time() - total_start_time
    logger.info(f"[Total Process Time] Complete downtime process took {total_time:.3f}s")
    print(f"[Total Process Time] Complete process took {total_time:.3f}s")
    
    return result


def getAllMachinesDetails():
    return   [
    {"machine_id": "FP001", "name": "FP001", "machine_type": "Finning", "list_seq": 1},
    {"machine_id": "FP002", "name": "FP002", "machine_type": "Finning", "list_seq": 2},
    {"machine_id": "FP003", "name": "FP003", "machine_type": "Finning / Fin Punching", "list_seq": 3},
    {"machine_id": "FP005", "name": "FP005", "machine_type": "Finning / Fin Punching", "list_seq": 4},
    {"machine_id": "FP006", "name": "FP006", "machine_type": "Finning", "list_seq": 5},
    {"machine_id": "FP007", "name": "FP007", "machine_type": "Finning / Fin Punching", "list_seq": 6},
    {"machine_id": "FP008", "name": "FP008", "machine_type": "Finning", "list_seq": 7},
    {"machine_id": "SM001", "name": "SM001", "machine_type": "Shearing", "list_seq": 8},
    {"machine_id": "SM002", "name": "SM002", "machine_type": "Shearing", "list_seq": 9},
    {"machine_id": "CNCMC002", "name": "CNCMC002", "machine_type": "Punching", "list_seq": 10},
    {"machine_id": "CNCMC003", "name": "CNCMC003", "machine_type": "Punching", "list_seq": 11},
    {"machine_id": "BB001", "name": "BBD01", "machine_type": "Bending", "list_seq": 12},
    {"machine_id": "YSDCNC001", "name": "VSDCNO 001", "machine_type": "Bending", "list_seq": 13},
    {"machine_id": "VBHB001", "name": "VBHB001", "machine_type": "Hairpin bend", "list_seq": 14},
    {"machine_id": "VBHB002", "name": "VBHB002", "machine_type": "Hairpin bend", "list_seq": 15},
    {"machine_id": "VBHB003", "name": "VBHB003", "machine_type": "Hairpin bend", "list_seq": 16},
    {"machine_id": "T001", "name": "T001", "machine_type": "Cut to length", "list_seq": 17},
    {"machine_id": "T002", "name": "T002", "machine_type": "Cut to length", "list_seq": 18},
    {"machine_id": "VEMCO01", "name": "VEMCO01", "machine_type": "Cut to length", "list_seq": 19},
    {"machine_id": "VEMCO02", "name": "VEMCO02", "machine_type": "Cut to length", "list_seq": 20},
    {"machine_id": "VEMC001", "name": "VEMC001", "machine_type": "Expansion", "list_seq": 21},
    {"machine_id": "FB003", "name": "FB003", "machine_type": "Expansion", "list_seq": 22},
    {"machine_id": "FB004", "name": "FB004", "machine_type": "Expansion", "list_seq": 23},
    {"machine_id": "FB005", "name": "FB005", "machine_type": "Expansion", "list_seq": 24},
    {"machine_id": "FB006", "name": "FB006", "machine_type": "Expansion", "list_seq": 25},
    {"machine_id": "HB001", "name": "HB001", "machine_type": "Expansion", "list_seq": 26},
    {"machine_id": "VEMC002", "name": "VEMC002", "machine_type": "Expansion", "list_seq": 26},
    {"machine_id": "TF001", "name": "TF001", "machine_type": "Trimming & Flaring", "list_seq": 27},
    {"machine_id": "RBL001", "name": "RBL001", "machine_type": "Return Bend Loading", "list_seq": 28},
    {"machine_id": "RBB001", "name": "RBB001", "machine_type": "Return Bend Brazing", "list_seq": 29},
    {"machine_id": "BBMCO02", "name": "BBMCO02", "machine_type": "Coil Bending", "list_seq": 30},
    {"machine_id": "AWMCO01", "name": "AWMCO01", "machine_type": "Coil Bending", "list_seq": 31},
    {"machine_id": "PC001", "name": "PC001", "machine_type": "Header Cutting", "list_seq": 32},
    {"machine_id": "TBMC001", "name": "TBMC001", "machine_type": "Header Bending", "list_seq": 33},
    {"machine_id": "IBCMC001", "name": "IBCMC001", "machine_type": "Header Bending", "list_seq": 34},
    {"machine_id": "HBDMC001", "name": "HBDMC001", "machine_type": "Header Drilling", "list_seq": 35},
    {"machine_id": "CNCMC001", "name": "CNCMC001", "machine_type": "Header Drilling", "list_seq": 36},
    {"machine_id": "CNCDMC001", "name": "CNCDMC001", "machine_type": "Header Drilling", "list_seq": 37},
    {"machine_id": "TESMC001", "name": "TESMC001", "machine_type": "Header End Closing", "list_seq": 38},
    {"machine_id": "TESMC002", "name": "TESMC002", "machine_type": "Header End Closing", "list_seq": 39},
    {"machine_id": "TD001", "name": "TD001", "machine_type": "Header Branching", "list_seq": 39},
    {"machine_id": "H001", "name": "BP001", "machine_type": "Header Hole Piercing", "list_seq": 40},
    {"machine_id": "JDM01", "name": "JDM01", "machine_type": "Feeder Cut", "list_seq": 41},
    {"machine_id": "Manual001", "name": "Manual 001", "machine_type": "Header Sub Assembly", "list_seq": 42},
    {"machine_id": "Manual002", "name": "Manual 002", "machine_type": "Header to Coil", "list_seq": 43},
    {"machine_id": "Tank1", "name": "Tank 1", "machine_type": "Leak Testing", "list_seq": 44},
    {"machine_id": "Tank2", "name": "Tank 2", "machine_type": "Leak Testing", "list_seq": 45},
    {"machine_id": "Tank3", "name": "Tank 3", "machine_type": "Leak Testing", "list_seq": 46},
    {"machine_id": "Tank-FCU", "name": "Tank - FCU", "machine_type": "Leak Testing", "list_seq": 47},
    {"machine_id": "DegreasingCS1", "name": "Degreasing CS1", "machine_type": "Coil Degreasing", "list_seq": 48},
    {"machine_id": "DegreasingCS2", "name": "Degreasing CS2", "machine_type": "Coil Degreasing", "list_seq": 49},
    {"machine_id": "Booth1", "name": "Booth1", "machine_type": "Coating", "list_seq": 50},
    {"machine_id": "Booth2", "name": "Booth2", "machine_type": "Coating", "list_seq": 51},
    {"machine_id": "Booth3", "name": "Booth3", "machine_type": "Coating", "list_seq": 52},
    {"machine_id": "FP004", "name": "FP004", "machine_type": "Finning / Fin Punching", "list_seq": 53},
    {"machine_id": "BBMCO02", "name": "BBMCO02", "machine_type": "Coil Bending", "list_seq": 54},
    {"machine_id": "RBB001", "name": "RBB001", "machine_type": "Coil Bending", "list_seq": 55},
    {"machine_id": "AWMCO01", "name": "AWMCO01", "machine_type": "Coil Bending", "list_seq": 56}
  ]