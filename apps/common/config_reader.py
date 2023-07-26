import configparser
import pathlib
import logging
import os
import secrets


from apps.common import utils, constants, custom_exceptions, config_reader

config_data: configparser.ConfigParser = None


def read_config(env, app_base_dir):
    global config_data
    config = configparser.ConfigParser()
    config_file_path = app_base_dir + "/config-files/" + env + "/citadel-web-config.ini"
    logging.info(os.path.abspath(config_file_path))
    if os.path.exists(config_file_path):
        logging.info("Reading app config from - %s", config_file_path)
        config.read(config_file_path)
        config_data = config
    else:
        logging.error(
            "No config file found for env '%s' in the default config folder. Was looking for file '%s'",
            env,
            config_file_path,
        )
        raise custom_exceptions.MissingConfigException()
    
    #add app_base_dir to config data
    config_data.set("Main", "app_base_dir", app_base_dir)


def get_flask_config():
    config_data.set("Flask-Config", "SESSION_COOKIE_HTTPONLY", True)
