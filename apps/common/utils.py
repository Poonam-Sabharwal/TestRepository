import logging
import os
from apps.common import config_reader
from apps.common.custom_exceptions import MissingDocumentTypeException


def string_is_not_empty(input_str):
    return str is not None and len(input_str) > 0


def is_env_local():
    if config_reader.config_data.has_option("Main", "env"):
        env = config_reader.config_data.get("Main", "env")
    else:
        env = "local"

    return env.lower() == "local".lower()


def get_document_type_from_file_name(file_path):
    """
    get_document_type_from_file_name Takes a filename or absolute path and extracts the
    document type form the last part of the base filename.

    e.g file_path = "/Users/xyz/Citadel-IDP-App/local-blob-storage/test-company/VALIDATION-SUCCESSFUL/1001-receipt.jpg" OR

    file_path = "../VALIDATION-SUCCESSFUL/1001-receipt.jpg" OR

    file_path = "1001-receipt.jpg"

    Should extract "receipt" as the result. Using this value as key in config, finds the
    corresponding form recognizer model for this file.

    Args:
        file_path (str): the filename or path to extract the info from.

    Raises:
        MissingDocumentTypeException: Raised if the document type cannot be inferred from the provided file_path
        or there is no form recognizer mapping in config for the inferred document type.

    Returns:
        tuple(str): the first element is the inferred document type and second element is the mapped form recognizer model.
    """

    full_file_name = os.path.basename(file_path)
    name_part = os.path.splitext(full_file_name)[0]
    index = name_part.rfind("-")
    if index == -1:
        # there was no - in the filename part. could be missing there.
        msg = f"File name path {file_path} has no hyphen (-) in it. Was expecting one."
        logging.warning(msg)
        raise MissingDocumentTypeException(msg)

    document_type = name_part[(index + 1) :]
    found = False
    if config_reader.config_data.has_section("Form-Recognizer-Document-Types"):
        for key, value in config_reader.config_data.items("Form-Recognizer-Document-Types"):
            if str(document_type).lower() == str(key).lower():
                return document_type, value

    if not found:
        msg = f"Could not find form recognizer model for document type {document_type} inferred form file name path {file_path}."
        logging.error(msg)
        raise MissingDocumentTypeException(msg)
