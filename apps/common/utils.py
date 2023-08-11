import logging
from datetime import datetime
import os
from apps.common import config_reader,constants
from apps.common.custom_exceptions import MissingDocumentTypeException,MissingConfigException
import base64
from common.data_objects import Metadata
from azure.storage.blob import BlobServiceClient
countries_dict = {
    "-1": "Select a Country",
    "US": "United States",
    "CA": "Canada",
}

us_states_dict = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "FM": "Federated States of Micronesia",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MH": "Marshall Islands",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MP": "Northern Mariana Islands",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "PW": "Palau",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VI": "Virgin Islands",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}

ca_states_dict = {
    "AB": "Alberta",
    "BC": "British Columbia",
    "MB": "Manitoba",
    "NB": "New Brunswick",
    "NL": "Newfoundland",
    "NS": "Nova Scotia",
    "NT": "Northwest Territories",
    "NU": "Nunavut",
    "ON": "Ontario",
    "PE": "Prince Edward Island",
    "QC": "Quebec",
    "SK": "Saskatchewan",
    "YT": "Yukon",
}

def connect_str():
    if not config_reader.config_data.has_option("Main", "azure-storage-account-connection-str"):
        raise MissingConfigException("Main.azure-storage-account-connection-str is missing in config.")
    azure_storage_account_connection_str = config_reader.config_data.get("Main", "azure-storage-account-connection-str")
    if not string_is_not_empty(azure_storage_account_connection_str):
        raise MissingConfigException("Main.azure-storage-account-connection-str is present but has empty value.")
    if azure_storage_account_connection_str.startswith(("'", '"')) and azure_storage_account_connection_str.endswith(
        ("'", '"')
    ):
        azure_storage_account_connection_str = azure_storage_account_connection_str.strip("'\"")
    return azure_storage_account_connection_str


def string_is_not_empty(input_str):
    return (input_str is not None) and len(input_str) > 0


def is_env_local():
    if config_reader.config_data.has_option("Main", "env"):
        env = config_reader.config_data.get("Main", "env")
    else:
        env = "local"
        
    return env.lower() == "local".lower()


# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split("/")[-1]
        if segment == "":
            segment = "index"
        return segment
    except:
        return None


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
    
def blob_service_client():
    """
    blob_service_client calls BobServiceClient

    Returns:
        BobServiceClient
    """
    return BlobServiceClient.from_connection_string(connect_str())

def container_client():
    """
    container_client calls ContainerClient

    Returns:
        ContainerClient
    """
    return blob_service_client().get_container_client(constants.DEFAULT_BLOB_CONTAINER)

def get_metadata(status: str, path: str):
    """
    get_meta takes file status and its path and collects metadata properties of that blob.

    Args:
        status (str): Blob status
        path (str): Path of blob
    Returns:
      str:  returns object of class Metadata
    """
    blob_client = container_client().get_blob_client(path)
    properties = blob_client.get_blob_properties()

    md = Metadata()
    
    md.status = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}-{status}]"
    md.name = properties.name
    md.content_md5 = base64.b64encode(properties.content_settings.content_md5).decode("utf-8")
    md.url = blob_client.url
    md.blob_type = properties.blob_type
    md.container = container_client().container_name
    md.content_length = properties.size
    md.created = properties.creation_time.strftime("%Y-%m-%d %H:%M:%S")
    md.last_modified = properties.last_modified.strftime("%Y-%m-%d %H:%M:%S")
    md.content_type = properties.content_settings.content_type
    
    return md

############################################







