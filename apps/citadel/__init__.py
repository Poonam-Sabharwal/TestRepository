# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - Aark Global
"""

from flask import Blueprint, render_template
from flask_login import login_manager
from apps import login_manager

citadel_blueprint = Blueprint("citadel_blueprint", __name__, url_prefix="/citadel")


# Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template("home/page-403.html"), 403


@citadel_blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template("home/page-403.html"), 403


@citadel_blueprint.errorhandler(404)
def not_found_error(error):
    return render_template("home/page-404.html"), 404


@citadel_blueprint.errorhandler(500)
def internal_error(error):
    return render_template("home/page-500.html"), 500
