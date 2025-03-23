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
        logging.warning(f"Missing Python modules: {', '.join(missing_modules)}")
        return missing_modules
    else:
        logging.info("All required Python modules are installed.")
        return []

# Check if required external commands are available
def check_external_commands():
    missing_commands = [cmd for cmd in REQUIRED_COMMANDS if which(cmd) is None]

    if missing_commands:
        logging.warning(f"Missing external commands: {', '.join(missing_commands)}")
        return missing_commands
    else:
        logging.info("All required external commands are available.")
        return []

# Check if required directories exist
def check_directories():
    missing_directories = []
    for directory in [LOG_DIR, LOCK_DIR]:
        if not os.path.exists(directory):
            logging.warning(f"Missing directory: {directory}")
            missing_directories.append(directory)
        else:
            logging.info(f"Directory exists: {directory}")

    return missing_directories

# Check if required files exist
def check_files():
    missing_files = []
    for file_path in [CONFIG_FILE, INPUT_FILE]:
        if not os.path.isfile(file_path):
            logging.warning(f"Missing file: {file_path}")
            missing_files.append(file_path)
        else:
            logging.info(f"File exists: {file_path}")

    return missing_files

# Validate configuration file
def validate_config():
    try:
        import yaml
        with open(CONFIG_FILE, "r") as file:
            config = yaml.safe_load(file)

        errors = []
        if not config.get("ENV_URI") or not config.get("Api_Token"):
            errors.append("Missing 'ENV_URI' or 'Api_Token' in configuration file.")

        if not config.get("functions"):
            errors.append("Missing 'functions' in configuration file.")

        if errors:
            logging.warning("Configuration file errors:")
            for error in errors:
                logging.warning(error)
            return errors
        else:
            logging.info("Configuration file is valid.")
            return []
    except Exception as e:
        logging.warning(f"Error validating configuration file: {e}")
        return [str(e)]

if __name__ == "__main__":
    setup_logging()

    logging.info("Starting prerequisite checks...")

    # Perform checks
    missing_modules = check_python_modules()
    missing_commands = check_external_commands()
    missing_directories = check_directories()
    missing_files = check_files()
    config_errors = validate_config()

    # Summarize results
    logging.info("\n=== Prerequisite Check Summary ===")

    if missing_modules:
        logging.info(f"Missing Python modules: {', '.join(missing_modules)}")
        logging.info(f"To install missing modules, run: pip install {' '.join(missing_modules)}")

    if missing_commands:
        logging.info(f"Missing external commands: {', '.join(missing_commands)}")
        logging.info("Please install the missing commands using your package manager (e.g., apt, yum, or brew).")

    if missing_directories:
        logging.info(f"Missing directories: {', '.join(missing_directories)}")

    if missing_files:
        logging.info(f"Missing files: {', '.join(missing_files)}")

    if config_errors:
        logging.info("Configuration file errors:")
        for error in config_errors:
            logging.info(f"- {error}")

    if not (missing_modules or missing_commands or missing_directories or missing_files or config_errors):
        logging.info("All prerequisite checks passed. You can now run your script.")
    else:
        logging.info("Prerequisite checks completed with warnings. Please address the above issues.")

