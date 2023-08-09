# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import logging
from apps.common import logging_config, constants, config_reader

# Load the logging and config reader before anything else
app_base_dir = os.path.abspath(os.path.dirname(__file__))
logging_config.configure_logging(os.path.abspath(constants.DEFAULT_LOG_FILE_PATH))

config_reader.read_config("local", app_base_dir)

# continue further now
from flask_minify import Minify
from sys import exit
from apps.flask_config import config_dict
from apps import create_app


# WARNING: Don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

# The configuration
get_config_mode = "Debug" if DEBUG else "Production"

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit("Error: Invalid <config_mode>. Expected values [Debug, Production] ")

app = create_app(app_config)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

logging.info("App base directory: %s", app_base_dir)
logging.info("App Env: %s", config_reader.config_data.get("Main", "env"))
logging.info("Flask Debug Mode: %s", str(DEBUG))
logging.info("Flask Page Compression: %s", ("False" if DEBUG else "True"))
logging.info("Database Connection String: %s", config_reader.config_data.get("Main", "mongodb-connection-string"))
logging.info("Flask Asset Root: %s", app_config.ASSETS_ROOT)

if __name__ == "__main__":
    app.run()
