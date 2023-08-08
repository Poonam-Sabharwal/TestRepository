import logging


# TODO: add a separate file based log handler for werkzeug url access logs.
# see https://stackoverflow.com/questions/42797276/flask-how-to-write-werkzeug-logs-to-log-file-using-rotatingfilehandler
def configure_logging(logFileAbsPath):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)-8s] [%(filename)s:%(lineno)s] - %(message)s",
        handlers=[logging.FileHandler(logFileAbsPath), logging.StreamHandler()],
    )

    # set the azure python sdk logger level to info
    logging.getLogger("azure.core.pipeline.policies").setLevel(logging.WARNING)

    return logging.getLogger(__name__)
