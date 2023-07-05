import logging

from pythonjsonlogger import jsonlogger
from starlette.requests import Request

# from app.utils.config import settings
#
# ENV_NAME = settings.ENV_NAME
# LAMBDA_INIT_TYPE = settings.AWS_LAMBDA_INITIALIZATION_TYPE


logger = logging.getLogger()
logger.setLevel(logging.INFO)
del logger.handlers[:]  # Remove any default handlers
formatter = jsonlogger.JsonFormatter("%(asctime) %(levelname) %(message)")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def log_request(request: Request):
    log = {
        "log_type": "incoming_http_request",
        "path_params": request.path_params,
        "query_params": request.query_params,
        "path": request.url.path,
        "method": request.method,
        "headers": request.headers,
        "aws_event": request.scope.get("aws.event"),
    }
    logger.info(log)
