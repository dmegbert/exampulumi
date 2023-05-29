from mangum import Mangum

from src.main import app


def handle_event(event, context):
    asgi_handler = Mangum(app=app, lifespan="off")
    resp = asgi_handler(event, context)
    return resp
