
from datetime import datetime, timedelta
import os
from flask import Flask,  request, jsonify
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
from pocketbase import getAndTransformJobData,getAndTransformDowntimes, getAndTransformScheduledJobs,getAllMachinesDetails
from schedule import Job, Operation, Machine, Downtime, ScheduledJob, validate_scheduling_input, choose_scheduling_approach

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # Allows all origins (replace with specific domains if needed)
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

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



@app.route('/api/routes', methods=['POST'])
def get_routes():
    # Expect a JSON payload with a list of job numbers
    try:
        data = request.get_json()
    # Today's date in ISO format
        today_date = datetime(2025, 7, 6).strftime("%Y-%m-%dT%H:%M:%S")
    except Exception as e:
        logger.error(f"[Input Error] Failed to parse JSON: {str(e)}")
        return jsonify({"error": "Invalid JSON format"}), 400

    # Call main with the list of job numbers
    result = getAndTransformDowntimes(today_date)
    return jsonify(result)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True, use_reloader=False)
