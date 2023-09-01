import os, logging
from flask import make_response, jsonify
from bson import json_util
from flask.wrappers import Request, Response
from werkzeug.utils import secure_filename
from mongoengine.queryset.visitor import Q
from apps.models.input_blob_model import LifecycleStatusTypes, MetaData, LifecycleStatus, InputBlob
from apps.common import utils
from apps.common.custom_exceptions import CitadelIDPWebException, DocumentNotFoundException


def get_input_document_blobs_by_row_id(row_id) -> InputBlob:
    document = InputBlob().objects(id=row_id).first()
    return document


def handle_document_toggle_activate_delete(document_id, action):
    document: InputBlob = InputBlob.objects(pk=document_id).first()
    old_value = False
    new_value = False
    if document:
        if action.lower() == "is_active":
            old_value = document.is_active
            if old_value:
                document.is_active = False
                new_value = False
            else:
                document.is_active = True
                new_value = True
        else:
            raise CitadelIDPWebException(f"Invalid toggle action '{action}' requested.")
        document.save()
        logging.info("Successfully toggled '%s' from %s to %s", action, old_value, new_value)
    else:
        msg = f"toggle activate operation failed. No document found with id {document_id}"
        raise DocumentNotFoundException(msg)


def prepare_document_list_data(draw, search_value, start_index, page_length):
    """
    prepare_document_list_data _summary_
    Args:
        draw (_type_): _description_
        search_value (_type_): _description_
        page_start (int): zero based page number. i.e. page 0 means its page 1
        page_length (int): number of records to fetch per page.
    """
    end_index = start_index + page_length
    document_data = None
    records_total = InputBlob.objects().count()
    records_filtered = records_total
    if utils.string_is_not_empty(search_value):
        document_data = InputBlob.objects(Q(blob_name__icontains=search_value))[start_index:end_index]
        # get the count of records also
        records_filtered = InputBlob.objects(Q(blob_name__icontains=search_value)).count()
    else:
        document_data = InputBlob.objects[start_index:end_index]
    # logging.info(document_data)
    response_data = []
    for document in document_data:
        size_in_mb = document.metadata.content_length_bytes / (1024 * 1024)
        document_type_size = f"{size_in_mb:.2f} MB, {document.metadata.content_type}"
        user_full_name = f" {document.uploader_user.first_name}"
        if utils.string_is_not_empty(document.uploader_user.middle_name):
            user_full_name += f" {document.uploader_user.middle_name}"
        user_full_name += f"{document.uploader_user.last_name}"
        last_status = document.lifecycle_status_list[-1]
        final_status = f"{last_status.status.name} , {last_status.updated_date_time}"
        response_data.append(
            {
                "DT_RowId": str(document.pk),
                "document_name": document.blob_name,
                "uploaded_by": user_full_name,
                "document_type_size": document_type_size,
                "created_date": document.date_created,
                "last_modified_date": document.date_last_modified,
                "status": final_status,
                "is_active": "Yes" if (document.is_active) else "No",
            }
        )
    response = {
        "draw": draw,
        "recordsFiltered": records_filtered,
        "recordsTotal": records_total,
        "data": response_data,
    }
    # logging.info("response -> %s", response)
    return jsonify(response)
