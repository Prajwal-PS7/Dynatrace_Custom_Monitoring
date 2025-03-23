import os
import sys
import subprocess
import logging
from shutil import which

# Define constants for directories and files
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(HOME_DIR, "logs")
LOCK_DIR = os.path.join(HOME_DIR, "locks")
CONFIG_FILE = os.path.join(HOME_DIR, "config.yaml")
INPUT_FILE = os.path.join(HOME_DIR, "input_file.txt")
UTILS_FILE = os.path.join(HOME_DIR, "../UTILS/utils.yaml")

# List of required Python modules
REQUIRED_MODULES = [
    "subprocess", "json", "sys", "os", "yaml", "logging", "datetime", "re", "fcntl"
]

# List of required external commands
REQUIRED_COMMANDS = ["curl"]

# Setup logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

# Check if required Python modules are installed
def check_python_modules():
    missing_modules = []
    for module in REQUIRED_MODULES:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        logging.error(f"Missing Python modules: {', '.join(missing_modules)}")
        sys.exit(1)
    else:
        logging.info("All required Python modules are installed.")

# Check if required external commands are available
def check_external_commands():
    missing_commands = [cmd for cmd in REQUIRED_COMMANDS if which(cmd) is None]

    if missing_commands:
        logging.error(f"Missing external commands: {', '.join(missing_commands)}")
        sys.exit(1)
    else:
        logging.info("All required external commands are available.")

# Check if required directories exist
def check_directories():
    for directory in [LOG_DIR, LOCK_DIR]:
        if not os.path.exists(directory):
            logging.error(f"Missing directory: {directory}")
            sys.exit(1)
        else:
            logging.info(f"Directory exists: {directory}")

# Check if required files exist
def check_files():
    for file_path in [CONFIG_FILE, INPUT_FILE]:
        if not os.path.isfile(file_path):
            logging.error(f"Missing file: {file_path}")
            sys.exit(1)
        else:
            logging.info(f"File exists: {file_path}")

# Validate configuration file
def validate_config():
    try:
        import yaml
        with open(CONFIG_FILE, "r") as file:
            config = yaml.safe_load(file)

        if not config.get("ENV_URI") or not config.get("Api_Token"):
            logging.error("Configuration file is missing 'ENV_URI' or 'Api_Token'.")
            sys.exit(1)

        if not config.get("functions"):
            logging.error("Configuration file is missing 'functions'.")
            sys.exit(1)

        logging.info("Configuration file is valid.")
    except Exception as e:
        logging.error(f"Error validating configuration file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_logging()

    logging.info("Starting prerequisite checks...")

    # Perform checks
    check_python_modules()
    check_external_commands()
    check_directories()
    check_files()
    validate_config()

    logging.info("All prerequisite checks passed. You can now run your script.")

