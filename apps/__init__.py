# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import logging

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from pathlib import Path
from prettytable import PrettyTable

from apps.common import config_reader


db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app: Flask):
    # ---- register citadel blueprints
    from apps.citadel import citadel_blueprint as citadel_blueprint_parent_module

    # scan the citadel blueprints folder for all child blueprints and register them to citadel_blueprint_parent
    app_base_dir = config_reader.config_data.get("Main", "app_base_dir")
    citadel_blueprints_parent_folder = Path(app_base_dir + "/apps/citadel").absolute()
    for child_blueprint_item in os.scandir(citadel_blueprints_parent_folder):
        if child_blueprint_item.is_dir() and not child_blueprint_item.name.startswith("__"):
            logging.info("Registering '%s' blueprint.", child_blueprint_item.name)
            child_blueprint_module = import_module(f"apps.citadel.{child_blueprint_item.name}.routes")
            citadel_blueprint_parent_module.register_blueprint(child_blueprint_module.blueprint)
    app.register_blueprint(citadel_blueprint_parent_module)

    # -- register the other blueprints that came with sample apps
    for module_name in ("authentication", "home"):
        module = import_module("apps.{}.routes".format(module_name))
        app.register_blueprint(module.blueprint)

    # log the registered routes as a table
    pt = PrettyTable()
    pt.align = "l"
    pt.field_names = ["Route", "HTTP Methods", "Handler"]
    for route in app.url_map.iter_rules():
        pt.add_row([route.rule, route.methods, route.endpoint])
        # logging.info("Route: '%s', HTTP Methods: %s, Handler: '%s'", route.rule, route.methods, route.endpoint)
    logging.info("Following routes registered successfully:\n%s", pt.get_string())


def configure_database(app):
    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:
            print("> Error: DBMS Exception: " + str(e))

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
                basedir, "db.sqlite3"
            )

            print("> Fallback to SQLite ")
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
