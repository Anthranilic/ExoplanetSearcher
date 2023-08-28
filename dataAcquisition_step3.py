import os
import logging
import json
import requests

# Custom Exception
class DataAcquisitionError(Exception):
    """Exception raised for errors in the data acquisition process."""
    pass

# Constants
API_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+ps&format=json"
JSON_FILE_PATH = "/../output_data.json"
CONFIG_FILE_PATH = "path_to_your_config_file.json"

# Set up Logging
def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Logging initialized.")

def fetch_data_from_api(api_url: str, timeout=300) -> dict:
    try:
        response = requests.get(api_url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from API: {str(e)}")
        raise DataAcquisitionError(f"API Error: {str(e)}")

def save_data_to_json(data: dict, file_path: str) -> bool:
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"Error saving data to .json file: {str(e)}")
        raise DataAcquisitionError(f"File Save Error: {str(e)}")

def load_config(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file {file_path} not found.")
        raise DataAcquisitionError(f"Configuration file not found: {file_path}")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {file_path}.")
        raise DataAcquisitionError(f"JSON Decode Error for {file_path}")
    except Exception as e:
        logging.error(f"Failed to load configuration: {str(e)}")
        raise DataAcquisitionError(f"Unknown Configuration Load Error: {str(e)}")

def check_existing_data(file_path: str) -> bool:
    if os.path.exists(file_path):
        choice = input(f"{file_path} already exists. Do you want to use the existing one? (yes/no): ")
        if choice.lower() == "yes":
            return True
    return False

if __name__ == "__main__":
    setup_logging()
    
    # Load configurations from the config.json file
    config_data = load_config("config.json")
    if not config_data:
        logging.error("Failed to load configuration.")
        raise DataAcquisitionError("Configuration file not loaded.")

    API_URL = config_data['api_url']
    JSON_FILE_PATH = config_data['json_output_path']
    TIMEOUT = config_data['api_timeout']

    if not check_existing_data(JSON_FILE_PATH):
        data = fetch_data_from_api(API_URL, TIMEOUT)
        if data:
            success = save_data_to_json(data, JSON_FILE_PATH)
            if success:
                logging.info(f"Data saved successfully to {JSON_FILE_PATH}")
            else:
                logging.error("Failed to save data.")
        else:
            logging.error("Failed to fetch data from API.")
