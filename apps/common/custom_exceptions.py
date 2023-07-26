"""
    This module contains the list of all custom exceptions for Citadel IDP
"""


class CitadelIDPWebException(Exception):
    """
    Generic Citadel IDP Web Exception to be raised for any high level processing failures.
    """


class MissingConfigException(CitadelIDPWebException):
    """
    Exception to be raised when some config is missing or empty.
    """


class MissingDocumentTypeException(CitadelIDPWebException):
    """
    Exception to be raised when document type cannot be inferred from file name.
    """