import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from datetime import datetime,timedelta
import random
import logging
from logging.handlers import RotatingFileHandler

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

def get_filtered_records(collection_name, auth_token, filter_query="", page=1, per_page=50):
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


def getJobDetails(auth_token, filter_query=""):
    collection_name = f"{PLANT_CODE}_jobDetails"
    url = f"{PB_BASE_URL}/api/collections/{collection_name}/records"
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    all_records = []
    page = 1
    per_page = 50  # Pocketbase default per page limit

    while True:
        params = {
            "page": page,
            "perPage": per_page
        }
        if filter_query:
            params["filter"] = filter_query

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            records = data.get("items", [])
            all_records.extend(records)

            # Check if there are more pages
            if not records or len(records) < per_page or page >= data.get("totalPages", 1):
                break  # Exit loop if no more records or last page reached

            page += 1  # Move to the next page

        except requests.RequestException as e:
            error_details = f"Failed to fetch job details from collection {collection_name} with filter '{filter_query}' on page {page}. Error: {str(e)}"
            log_detailed_error("Fetch Job Details", "Job details retrieval failed", error_details)
            logger.error(f"[Fetch Job Details Error] {e}")
            return all_records  # Return whatever was fetched before the error

    return all_records


def getOperationsByJobID(auth_token, jobNumber):

    collection_name = f"{PLANT_CODE}_jobProductReceipeRoutes"
    url = f"{PB_BASE_URL}/api/collections/{collection_name}/records"
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    all_records = []
    page = 1
    per_page = 50  # Pocketbase default per page limit
    filter_query = f"jobNumber='{jobNumber}'"

    while True:
        params = {
            "page": page,
            "perPage": per_page,
            "filter": filter_query
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            print(response.status_code)
            response.raise_for_status()
            data = response.json()
            records = data.get("items", [])
            all_records.extend(records)

            # Check if there are more pages
            if not records or len(records) < per_page or page >= data.get("totalPages", 1):
                break  # Exit loop if no more records or last page reached

            page += 1  # Move to the next page

        except requests.RequestException as e:
            error_details = f"Failed to fetch operations from collection {collection_name} for jobNumber '{jobNumber}' on page {page}. Error: {str(e)}"
            log_detailed_error("Fetch Operations", "Operation retrieval failed", error_details)
            logger.error(f"[Fetch Operations Error] {e}")
            return all_records  # Return whatever was fetched before the error

    return all_records


from datetime import datetime


def getAndTransformJobData(auth_token, jobNumber):
    collection_name = f"{PLANT_CODE}_receipeRouteMachines"
    url = f"{PB_BASE_URL}/api/collections/{collection_name}/records"
    print("this is url", url)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    all_records = []
    page = 1
    per_page = 40

    filter_query = f"jobreceipeId.jobId.jobNumber='{jobNumber}'"
    params = {
        "page": page,
        "perPage": per_page,
        "filter": filter_query,
        "expand": "jobreceipeId,jobreceipeId.jobId,machine",
        "sort": "-created"
    }

    try:
        while True:
            print(f"Fetching page {page} for jobNumber '{jobNumber}' from collection {collection_name}...")
            response = requests.get(url, headers=headers, params=params)
            print(f"Response status code: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            records = data.get("items", [])
            print(f"Fetched {len(records)} records from page {page} for jobNumber '{jobNumber}'")
            all_records.extend(records)

            if not records or len(records) < per_page or page >= data.get("totalPages", 1):
                break

            page += 1
            params["page"] = page

    except requests.RequestException as e:
        error_details = f"Failed to fetch machine records for jobNumber '{jobNumber}' from collection {collection_name}. Error: {str(e)}"
        log_detailed_error("Fetch Machine Records", "Retrieval failed", error_details)
        logger.error(f"[Fetch Machine Records Error] {e}")
        return None

    if not all_records:
        error_details = f"No machine records found for jobNumber '{jobNumber}' in collection {collection_name}"
        log_detailed_error("Fetch Machine Records", "No records found", error_details)
        return None

    job_data = {}
    for record in all_records:
        jobreceipe = record.get("expand", {}).get("jobreceipeId", {})
        job_details = jobreceipe.get("expand", {}).get("jobId", {})
        operation = jobreceipe

        if not job_details or not operation:
            continue

        job_number = job_details.get("jobNumber")
        if job_number not in job_data:
            job_data[job_number] = {
                "jobDetails": job_details,
                "operations": {}
            }

        operation_name = operation.get("operationName", "unknown")
        if operation_name not in job_data[job_number]["operations"]:
            job_data[job_number]["operations"][operation_name] = {
                "operationDetails": operation,
                "machines": []
            }

        machine_id = record.get("machineId", "unknown")
        cycle_time_str = record.get("cycleTime", "0")
        try:
            cycle_time = float(cycle_time_str)
        except (ValueError, TypeError):
            cycle_time = 0.0
        
        job_data[job_number]["operations"][operation_name]["machines"].append(
            (machine_id, cycle_time)
        )

    if jobNumber not in job_data:
        error_details = f"No job data found for jobNumber '{jobNumber}'"
        log_detailed_error("Transform Job Data", "No job data", error_details)
        return None

    job_info = job_data[jobNumber]
    job_details = job_info["jobDetails"]

    operations = []
    for op_name, op_data in job_info["operations"].items():
        operation = {
            "op_id": op_data["operationDetails"]["id"],
            "name": op_name,
            "possible_machines": op_data["machines"]
        }
        operations.append(operation)

    # Sort operations by sequence to maintain proper order
    operations.sort(key=lambda op: int(op_data["operationDetails"].get("sequence", "0")) if op_data["operationDetails"].get("sequence", "0").isdigit() else 0)

    schedule_start = datetime(2025, 6, 12, 0, 0, 0)
    delivery_date = schedule_start + timedelta(days=30)

    # Construct the output dictionary matching the template
    job_dict = {
        "job_id": int(job_details.get("jobNumber", 0)),  # Convert to int
        "quantity": int(job_details.get("jobQty", 0)) or 0,
        "delivery_date": delivery_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "priority": 0,  # Default priority as in original code
        "schedule_direction": "forward",  # Default as in original code
        "operations": operations
    }

    return job_dict

def main(job_numbers):
    auth_token = login_admin()
    if not auth_token:
        logger.error("[Main Error] Failed to authenticate with Pocketbase")
        return {"error": "Failed to authenticate with Pocketbase"}

    # Process each job number and collect results
    jobs = []
    for job_number in job_numbers:
        job = getAndTransformJobData(auth_token, job_number)
        if job is None:
            logger.warning(f"[Main Warning] No job found for jobNumber '{job_number}'")
            continue  # Skip to the next job number if this one fails
        jobs.append(job)

    return jobs