import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from datetime import datetime,timedelta
import logging
from logging.handlers import RotatingFileHandler
import time

# Load environment variables
load_dotenv()

PB_BASE_URL = os.getenv("PB_BASE_URL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
PLANT_CODE = "OCCUAT"
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
        cycle_time_str = record.get("cycleTime", "0")
        
        # Optimized type conversion
        try:
            cycle_time = float(cycle_time_str) if cycle_time_str else 0.0
        except (ValueError, TypeError):
            cycle_time = 0.0
        
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
            "start": record.get("scheduleStartTime", ""),
            "end": record.get("scheduleStopTime", "")
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
    
    filter_query = f"start_date>'{start_date_after}'"
    
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

def transformDowntimeData(raw_records):
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
                "machine_id": machine_id if machine_id else "unknown",
                "start": record.get("start_date", ""),
                "end": record.get("end_date", ""),
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
    result = transformDowntimeData(raw_records)
    transform_time = time.time() - transform_start
    print(f"After transforming data: {transform_time:.3f}s")
    
    total_time = time.time() - total_start_time
    logger.info(f"[Total Process Time] Complete downtime process took {total_time:.3f}s")
    print(f"[Total Process Time] Complete process took {total_time:.3f}s")
    
    return result


def getAllMachinesDetails():
    return   {"machines": [
    {"machine_id": "FP001", "name": "FP001", "cycle_time_per_unit": 62, "machine_type": "Finning", "list_seq": 1},
    {"machine_id": "FP002", "name": "FP002", "cycle_time_per_unit": 62, "machine_type": "Finning", "list_seq": 2},
    {"machine_id": "FP006", "name": "FP006", "cycle_time_per_unit": 55, "machine_type": "Finning", "list_seq": 3},
    {"machine_id": "FP008", "name": "FP008", "cycle_time_per_unit": 55, "machine_type": "Finning", "list_seq": 4},
    {"machine_id": "FP007", "name": "FP007", "cycle_time_per_unit": 62, "machine_type": "Finning", "list_seq": 39},
    {"machine_id": "FP005", "name": "FP005", "cycle_time_per_unit": 62, "machine_type": "Finning", "list_seq": 40},
    {"machine_id": "SM001", "name": "SM001", "cycle_time_per_unit": 30, "machine_type": "Shearing", "list_seq": 5},
    {"machine_id": "SM002", "name": "SM002", "cycle_time_per_unit": 30, "machine_type": "Shearing", "list_seq": 6},
    {"machine_id": "CNCMC002", "name": "CNCMC002", "cycle_time_per_unit": 0, "machine_type": "Punching", "list_seq": 7},
    {"machine_id": "CNCMC003", "name": "CNCMC003", "cycle_time_per_unit": 0, "machine_type": "Punching", "list_seq": 38},
    {"machine_id": "BB001", "name": "BB001", "cycle_time_per_unit": 0, "machine_type": "Bending", "list_seq": 8},
    {"machine_id": "YSDCNC001", "name": "YSDCNC001", "cycle_time_per_unit": 0, "machine_type": "Bending", "list_seq": 37},
    {"machine_id": "VBHB001", "name": "VBHB001", "cycle_time_per_unit": 0, "machine_type": "Hairpin Bend", "list_seq": 9},
    {"machine_id": "VBHB002", "name": "VBHB002", "cycle_time_per_unit": 0, "machine_type": "Hairpin Bend", "list_seq": 10},
    {"machine_id": "VBHB003", "name": "VBHB003", "cycle_time_per_unit": 0, "machine_type": "Hairpin Bend", "list_seq": 10},
    {"machine_id": "T001", "name": "T001", "cycle_time_per_unit": 0, "machine_type": "Cut to Length", "list_seq": 11},
    {"machine_id": "VEMC001", "name": "VEMC001", "cycle_time_per_unit": 0, "machine_type": "Expansion", "list_seq": 12},
    {"machine_id": "FB006", "name": "FB006", "cycle_time_per_unit": 0, "machine_type": "Expansion", "list_seq": 12},
    {"machine_id": "VEMC002", "name": "VEMC002", "cycle_time_per_unit": 0, "machine_type": "Expansion", "list_seq": 13},
    {"machine_id": "TF001", "name": "TF001", "cycle_time_per_unit": 0, "machine_type": "Trimming & Flaring", "list_seq": 14},
    {"machine_id": "RBL001", "name": "RBL001", "cycle_time_per_unit": 0, "machine_type": "Return Bend Loading", "list_seq": 15},
    {"machine_id": "RBB001", "name": "RBB001", "cycle_time_per_unit": 0, "machine_type": "Return Bend Brazing", "list_seq": 16},
    {"machine_id": "PC001", "name": "PC001", "cycle_time_per_unit": 0, "machine_type": "Header Cutting", "list_seq": 17},
    {"machine_id": "TBMC001", "name": "TBMC001", "cycle_time_per_unit": 0, "machine_type": "Header Bending", "list_seq": 18},
    {"machine_id": "HBDMC001", "name": "HBDMC001", "cycle_time_per_unit": 0, "machine_type": "Header Drilling", "list_seq": 19},
    {"machine_id": "CNCDMC001", "name": "CNCDMC001", "cycle_time_per_unit": 0, "machine_type": "Header Drilling", "list_seq": 20},
    {"machine_id": "TESMC001", "name": "TESMC001", "cycle_time_per_unit": 0, "machine_type": "Header End Closing", "list_seq": 21},
    {"machine_id": "TESMC002", "name": "TESMC002", "cycle_time_per_unit": 0, "machine_type": "Header End Closing", "list_seq": 22},
    {"machine_id": "TD001", "name": "TD001", "cycle_time_per_unit": 0, "machine_type": "Header Branching", "list_seq": 23},
    {"machine_id": "H001", "name": "H001", "cycle_time_per_unit": 0, "machine_type": "Header Hole Piercing", "list_seq": 24},
    {"machine_id": "T003", "name": "T003", "cycle_time_per_unit": 0, "machine_type": "Feeder Cut", "list_seq": 25},
    {"machine_id": "T002", "name": "T002", "cycle_time_per_unit": 0, "machine_type": "Feeder Cut", "list_seq": 26},
    {"machine_id": "Manual001", "name": "Manual 001", "cycle_time_per_unit": 0, "machine_type": "Header Sub Assembly", "list_seq": 27},
    {"machine_id": "Manual002", "name": "Manual 002", "cycle_time_per_unit": 0, "machine_type": "Header to Coil", "list_seq": 28},
    {"machine_id": "TankFCU", "name": "Tank FCU", "cycle_time_per_unit": 0, "machine_type": "Leak Testing", "list_seq": 29},
    {"machine_id": "Tank3", "name": "Tank 3", "cycle_time_per_unit": 0, "machine_type": "Leak Testing", "list_seq": 30},
    {"machine_id": "DegreasingCS1", "name": "Degreasing CS1", "cycle_time_per_unit": 0, "machine_type": "Coil Degreasing", "list_seq": 31},
    {"machine_id": "DegreasingCS2", "name": "Degreasing CS2", "cycle_time_per_unit": 0, "machine_type": "Coil Degreasing", "list_seq": 32},
    {"machine_id": "Booth1", "name": "Booth 1", "cycle_time_per_unit": 0, "machine_type": "Coating", "list_seq": 33},
    {"machine_id": "Booth2", "name": "Booth 2", "cycle_time_per_unit": 0, "machine_type": "Coating", "list_seq": 34},
    {"machine_id": "Booth3", "name": "Booth 3", "cycle_time_per_unit": 0, "machine_type": "Coating", "list_seq": 35}
  ]}