# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import logging
from flask import make_response, render_template, request, redirect, url_for, flash
from apps.citadel.list_all_documents import blueprint
from flask_login import login_required
from apps.common import utils
from apps.models.input_blob_model import InputBlob
from apps.services import list_all_documents_service
from apps.common.custom_exceptions import DocumentNotFoundException, CitadelIDPWebException
from mongoengine.errors import ValidationError

##########################################################################################
# APIs from here - these have /api prefixes
##########################################################################################


@blueprint.route("/api/get_list_document_data", methods=["POST"])
@login_required
def api_get_document_data():
    # Detect the current page
    segment = utils.get_segment(request)
    # logging.info("Request form is: %s", request.form)
    draw = request.form["draw"]
    page_number = int(request.form["start"])
    length = int(request.form["length"])
    search_value = request.form["search[value]"]
    # TODO: validate the request params
    response = list_all_documents_service.prepare_document_list_data(draw, search_value, page_number, length)
    # logging.info("response is -> %s", response)
    return make_response(response, 200)


@blueprint.route("/api/document_toggle_activate_delete", methods=["POST"])
@login_required
def toggle_document_status():
    document_id = request.form["document_id"]
    action = request.form["action"]
    if utils.string_is_not_empty(document_id) and utils.string_is_not_empty(action):
        try:
            list_all_documents_service.handle_document_toggle_activate_delete(document_id, action)
        except (CitadelIDPWebException, DocumentNotFoundException, ValidationError) as e:
            msg = f"Failed to toggle is active for document id {document_id}"
            logging.exception(msg)
            return make_response(msg, 404)
    else:
        return make_response("Missing document_id parameter.", 400)
    return make_response("Success, 200")


@blueprint.route(
    "/list_all_documents",
)
# @login_required
def show_list_all_documents():
    segment = utils.get_segment(request)
    """
    show_list_all_documents _summary_
    Returns:
        _type_: _description_
    """
    return render_template("citadel/list_all_documents.html", segment=segment)
