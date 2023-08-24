import os
import logging
import threading
import io
from flask import make_response, session
from http import HTTPStatus
from flask.wrappers import Request, Response
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, BlobType, BlobClient, ContentSettings
from concurrent.futures import ThreadPoolExecutor
from apps.common import utils, constants
from apps.common.custom_exceptions import CitadelIDPWebException
from apps.models.company_model import CompanyModel

folder_name = "Company-A"  # The name of the folder inside the container
subfolder_name = "Incoming"  # The name of the subfolder inside the folder


def __blob_exists(blob_client, blob_path):
    try:
        blob_client.get_blob_properties()
        return True
    except Exception:
        return False


def handle_document_upload(request: Request) -> Response:
    file_data = request.files["citadel_file_upload_dropper"]
    filename = secure_filename(file_data.filename)

    if file_data and filename:
        user_company_row_id = session.get(constants.SESSION_USER_COMPANY_ROW_ID)
        folder_name = f"{constants.COMPANY_ROOT_FOLDER_PREFIX}{user_company_row_id}"

        blob_service_client = BlobServiceClient.from_connection_string(utils.get_connection_string())

        container_client = blob_service_client.get_container_client(constants.DEFAULT_BLOB_CONTAINER)
        if not container_client.exists():
            # container_client.create_container()
            raise CitadelIDPWebException(
                f"Root Blog storage container {constants.DEFAULT_BLOB_CONTAINER} doesn't exist."
            )

        blob_path = os.path.join(folder_name, constants.INCOMING_FILES_FOLDER, filename)
        blob_client = blob_service_client.get_blob_client(container=constants.DEFAULT_BLOB_CONTAINER, blob=blob_path)

        current_chunk = int(request.form["dzchunkindex"])
        total_chunks = int(request.form["dztotalchunkcount"])

        # Adjust chunk size if provided in the request form data
        chunk_size = int(request.form["dzchunksize"])

        if chunk_size > constants.CHUNK_SIZE_BYTES:
            logging.error(
                "Received a chunk of size %s bytes which is more than the configured default chunk size of %s bytes from the incoming request.",
                chunk_size,
                constants.CHUNK_SIZE_BYTES,
            )
            return make_response(("Request data chunk size exceeds max allowed chunk size.", HTTPStatus.BAD_REQUEST))

        if current_chunk == 0:
            if __blob_exists(blob_client, blob_path):
                return make_response(("Document already exists.", HTTPStatus.BAD_REQUEST))
            else:
                blob_client.create_append_blob()

        # chunk_offset = current_chunk * chunk_size
        chunk_data = file_data.stream.read(chunk_size)
        blob_client.append_block(chunk_data)

        if current_chunk == total_chunks - 1:
            blob_properties = blob_client.get_blob_properties()
            if blob_properties.size != int(request.form["dztotalfilesize"]):
                return make_response(("Size mismatch", HTTPStatus.INTERNAL_SERVER_ERROR))
            logging.info("File %s has been uploaded successfully.", file_data.filename)
        # else:
        #     logging.info("Chunk %s of %s for file %s complete", current_chunk + 1, total_chunks, file_data.filename)

        return make_response(("Chunk upload successful", HTTPStatus.OK))

    else:
        msg = "Improper or incomplete request received. Either filename or the file data is missing."
        logging.error(msg)
        make_response(msg, HTTPStatus.BAD_REQUEST)
