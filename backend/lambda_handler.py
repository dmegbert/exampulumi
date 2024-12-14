from mangum import Mangum

from src.main import app


def handle_event(event, context):
    # Do not leave this in! 😱😱😱😱😱
    # This will run the migration every time the function is invoked
    # Migrations are no-ops if the database is already on the head migration
    # But its still a dumb way to have this configured and slow to attempt
    # a migration before handling every API request
    from alembic import command
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    # Do not leave this in! 😱😱😱😱😱

    asgi_handler = Mangum(app=app, lifespan="off")
    resp = asgi_handler(event, context)
    return resp
