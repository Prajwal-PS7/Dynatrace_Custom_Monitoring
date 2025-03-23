import subprocess
import json
import sys
import os
import yaml
import logging
from logging.handlers import TimedRotatingFileHandler
from fcntl import flock, LOCK_EX, LOCK_NB
from datetime import datetime, timedelta
import re

# Define HOME_DIR as the script's working directory
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(HOME_DIR, "logs")
LOCK_DIR = os.path.join(HOME_DIR, "locks")
INPUT_DIR = os.path.join(HOME_DIR, "input")
OUTPUT_DIR = os.path.join(HOME_DIR, "outfile")
UTILS_DIR = os.path.join(HOME_DIR, "../UTILS")

# Ensure logs and lock directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(LOCK_DIR, exist_ok=True)

# Setup logging
def setup_logging(config):
    log_level = config.get("log_level", "INFO").upper()
    log_file = os.path.join(LOG_DIR, "script.log")

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if log_level == "DEBUG" else logging.INFO)

    handler = TimedRotatingFileHandler(log_file, when="H", interval=1, backupCount=0)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logging.info(f"Logging initialized with level: {log_level}")

# Purge old logs
def purge_old_logs(log_dir, retention_days):
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


def copy_input_file_from_remote(server_ip, username, remote_path, local_path):
    """
    Copy input file from remote server using ssh command and process it locally
    """
    try:
        # Construct ssh command
        ssh_command = f"data_out=$(ssh {username}@{server_ip} \"cat {remote_path}\") ; echo \"$data_out\" | tee {local_path}"
        #scp_command = f"scp {username}@{server_ip}:{remote_path} {local_path}"
        logging.info(f"Executing SSH command: {ssh_command}")

        # Execute ssh command using older subprocess style
        process = subprocess.Popen(
            ssh_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Get output and error
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            logging.info("File transfer completed successfully")

            # Now, process the file with the given `cat -A` and `sed` pipeline
            process_cleanup = subprocess.Popen(
                f"cat -A {local_path} | sed -r 's/\^\[\[[0-9][a-zA-Z]\^\[\[[0-9]\;[0-9][0-9]m/ /g' | "
                f"grep '[A-Z]*.[0-9].[0-9][0-9]' | cut -d '.' -f 1 | uniq -c | tail -n +2 | tee {local_path}",
#                f"sed -r 's/\^\[\[[0-9][a-zA-Z]\^\[\[[0-9];[0-9][0-9];[0-9][0-9][a-zA-Z]/ /g' | sed -r 's/\$/ /g' | tee {local_path}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Get output and error from the cleanup process
            stdout_cleanup, stderr_cleanup = process_cleanup.communicate()

            if process_cleanup.returncode == 0:
                logging.info("File processed successfully")
                return True
            else:
                logging.error(f"Error processing file: {stderr_cleanup}")
                return False
        else:
            logging.error(f"SSH error: {stderr}")
            return False

    except Exception as e:
        logging.error(f"Error copying or processing file from remote server: {e}")
        return False

# Load configuration
def load_config(config_path):
    try:
        with open(config_path, "r") as file:
            logging.info("Loading configuration file.")
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        sys.exit(1)

# Parse input file
def parse_input_file(input_file):
    queue_data = {}
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()

        # Parse the lines of the input file and capture PID and Queue Names
        for line in lines:
            columns = line.split()
            if len(columns) >= 2:
                replica = columns[0]
                queuename = columns[1]
                queue_data[queuename] = {"replica": replica, "queuename": queuename}

    except Exception as e:
        logging.error(f"Error parsing input file: {e}")
        return {}
    return queue_data

# Send data to Dynatrace
def send_to_dynatrace(queue_data, env_uri, api_token, server, bankname):
    try:
        data = "\n".join([
            f"Host.whatsup,host={server},bankname={bankname},replica={status['replica']},queuename={status['queuename']} {status['replica']}"
            for queue, status in queue_data.items()
        ])

        command = (
            f"curl -k -X 'POST' '{env_uri}' "
            f"-H 'accept: application/json; charset=utf-8' "
            f"-H 'Authorization: Api-Token {api_token}' "
            f"-H 'Content-Type: text/plain; charset=utf-8' "
            f"-d '{data}' "
            f"--connect-timeout 10 --max-time 15"
        )

        logging.info(f"Executing curl command: {command}")
        result = subprocess.check_output(command, shell=True, universal_newlines=True)
        logging.info(f"Curl response: {result}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Curl subprocess error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error running curl: {e}")

# Ensure single instance
def ensure_single_instance(lock_file_path):
    try:
        lock_file = open(lock_file_path, "w")
        flock(lock_file, LOCK_EX | LOCK_NB)
        return lock_file
    except IOError:
        logging.error(f"Another instance of the function is already running: {lock_file_path}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Please specify the function name as an argument.")
        sys.exit(1)

    function_name = sys.argv[1]

    LOCK_FILE = os.path.join(LOCK_DIR, f"{function_name}.lock")
    lock_file = ensure_single_instance(LOCK_FILE)

    CONFIG_FILE = os.path.join(HOME_DIR, "config.yaml")
    config = load_config(CONFIG_FILE)

    setup_logging(config)

    retention_days = config.get("log_retention_days", 7)
    purge_old_logs(LOG_DIR, retention_days)

    # Check if 'functions' key exists and the function_name is in it
    if 'functions' not in config or function_name not in config['functions']:
        logging.error(f"Function '{function_name}' not found in config.yaml.")
        sys.exit(1)

    function_config = config['functions'][function_name]
    server = function_config['server']
    username = function_config['username']
    bankname = function_config['bankname']
    remote_input_file = function_config['remote_input_file']
    input_file = function_config['local_file']
    #input_file = os.path.join(HOME_DIR, "bc.txt")
    env_uri = config["ENV_URI"]
    api_token = config["Api_Token"]

    # Copy input file from remote server
    if not copy_input_file_from_remote(server, username, remote_input_file, input_file):
        logging.error("Failed to copy input file from remote server")
        sys.exit(1)

    # Parse input file and get queue data
    queue_data = parse_input_file(input_file)
    if queue_data:
        send_to_dynatrace(queue_data, env_uri, api_token, server, bankname)
    else:
        logging.error("No valid queue data found to send to Dynatrace")

    lock_file.close()
