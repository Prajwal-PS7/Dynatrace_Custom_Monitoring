import subprocess
import json
import sys
import os
import yaml
import logging
from logging.handlers import TimedRotatingFileHandler
from fcntl import flock, LOCK_EX, LOCK_NB
from datetime import datetime, timedelta

# Define HOME_DIR as the script's working directory
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(HOME_DIR, "logs")
LOCK_DIR = os.path.join(HOME_DIR, "locks")

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(LOCK_DIR, exist_ok=True)

def setup_logging(config):
    """Setup logging with configurable log level and rotation."""
    log_level = config.get("log_level", "INFO").upper()
    log_file = os.path.join(LOG_DIR, f"script.log")

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if log_level == "DEBUG" else logging.INFO)

    handler = TimedRotatingFileHandler(log_file, when="H", interval=1, backupCount=0)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logging.info(f"Logging initialized with level: {log_level}")
    logging.info("Log file will rotate hourly.")

def purge_old_logs(log_dir, retention_days):
    """Purge logs older than the specified number of days."""
    cutoff_time = datetime.now() - timedelta(days=retention_days)
    for file_name in os.listdir(log_dir):
        file_path = os.path.join(log_dir, file_name)
        if os.path.isfile(file_path):
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_time:
                try:
                    os.remove(file_path)
                    logging.info(f"Purged old log file: {file_path}")
                except Exception as e:
                    logging.error(f"Error purging log file {file_path}: {e}")

def load_config(config_path):
    """Load configuration from YAML file."""
    try:
        with open(config_path, "r") as file:
            logging.info("Loading configuration file.")
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        sys.exit(1)

def fetch_ps_data(server, username):
    """Fetch ps -ef data by executing a command remotely on the server."""
    try:
        logging.info(f"Fetching ps -ef data from server: {server}")
        command = f"ssh {username}@{server} ps -ef"
        result = subprocess.check_output(command, shell=True, universal_newlines=True)
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Subprocess error while fetching ps -ef data: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

def run_curl_command(env_uri, api_token, data_payload):
    """Run a curl command with a batch data payload."""
    try:
        command = (
            f"curl -k -X 'POST' '{env_uri}' "
            f"-H 'accept: application/json; charset=utf-8' "
            f"-H 'Authorization: Api-Token {api_token}' "
            f"-H 'Content-Type: text/plain; charset=utf-8' "
            f"-d '{data_payload}'"
        )

        # Print the command for debugging
        logging.info(f"Final curl command: {command}")

        result = subprocess.check_output(command, shell=True, universal_newlines=True)
        logging.info(f"Curl response: {result}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Curl subprocess error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error running curl: {e}")

def ensure_single_instance(lock_file_path):
    """Ensure only one instance of a specific function is running."""
    try:
        lock_file = open(lock_file_path, "w")
        flock(lock_file, LOCK_EX | LOCK_NB)
        return lock_file
    except IOError:
        logging.error(f"Another instance of the function is already running: {lock_file_path}")
        sys.exit(1)

def check_service_status(ps_data, service_name, pattern1, pattern2):
    """Check if both patterns are in the same line of ps -ef data."""
    service_status = 0  # Default: service is not running
    service_status_text = "Down"
    for line in ps_data.splitlines():
        if pattern1 in line and pattern2 in line:
            service_status = 1  # Service is running if both patterns are found in the same line
            service_status_text = "Up"
            logging.info(f"Service {service_name} is running. Found both patterns in line: {line}")
            break  # No need to continue if both patterns are found
    if service_status == 0:
        logging.info(f"Service {service_name} is not running. Patterns not found together.")
    return service_status

if __name__ == "__main__":
    # Get the function name passed as an argument
    if len(sys.argv) < 2:
        logging.error("Please specify the function name as an argument.")
        sys.exit(1)

    function_name = sys.argv[1]

    # Create a lock file path specific to the function name in LOCK_DIR
    LOCK_FILE = os.path.join(LOCK_DIR, f"{function_name}.lock")
    lock_file = ensure_single_instance(LOCK_FILE)

    # Configuration file path
    CONFIG_FILE = os.path.join(HOME_DIR, "config.yaml")

    # Load the configuration file
    config = load_config(CONFIG_FILE)

    # Setup logging
    setup_logging(config)

    # Purge old logs based on retention days
    retention_days = config.get("log_retention_days", 7)  # Default to 7 days
    purge_old_logs(LOG_DIR, retention_days)

    # Check if function exists in the configuration
    if function_name not in config['functions']:
        logging.error(f"Function '{function_name}' not found in config.yaml.")
        sys.exit(1)

    # Extract function-specific variables
    function_config = config['functions'][function_name]
    server = function_config['server']
    username = function_config['username']
    bankname = function_config['bankname'] 

    service_names = [function_config.get(f"service{i}") for i in range(1, 15) if f"service{i}" in function_config]
    patterns = {
        f"service{i}": {
            'pattern1': function_config.get(f"service{i}_pattern", ""),
            'pattern2': function_config.get(f"service{i}_pattern2", ""),
        }
        for i in range(1, 15)
        if f"service{i}" in function_config
    }

    env_uri = config["ENV_URI"]
    api_token = config["Api_Token"]

    # Fetch ps -ef data from the server
    ps_data = fetch_ps_data(server, username)

    # Save ps -ef data to a file
    output_file = os.path.join(HOME_DIR, f"outfile/ps_{server.replace('.', '_')}")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(ps_data)
    logging.info(f"ps -ef data saved to {output_file}")

    # Prepare a batch payload for all services
    data_payload = ""

    for service_name in service_names:
        # Get the patterns for the current service dynamically
        service_index = service_names.index(service_name) + 1  # Adjust the index for service1, service2, etc.
        pattern1 = patterns.get(f"service{service_index}", {}).get('pattern1', "")
        pattern2 = patterns.get(f"service{service_index}", {}).get('pattern2', "")

        # Default service status text (Down) until the service is found to be running
        service_status_text = "Down"
        service_status = 0  # Default service status to 1 (Down)

        # Proceed only if all required patterns are available
        if pattern1 and pattern2:
            # Check if the service is running by matching all patterns
            service_status = check_service_status(ps_data, service_name, pattern1, pattern2)

            # Update service_status_text based on the service status
            if service_status == 1:  # Service is running
                service_status_text = "Up"

            # Add service status to the data payload
            data_payload += f"XYZ.ABC,host={server},service={service_name},bankname={bankname},status={service_status_text} {service_status}\n"
        else:
            # Log the warning for missing patterns and treat the service as Down
            logging.warning(f"Missing pattern(s) for service {service_name}. Skipping.")
            data_payload += f"XYZ.ABC,host={server},service={service_name},status={service_status_text} {service_status}\n"

    # If there is any data to send, send it using the curl command
    if data_payload:
        run_curl_command(env_uri, api_token, data_payload.strip())

    # Release the lock file
    lock_file.close()

