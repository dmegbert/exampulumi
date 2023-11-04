import datetime
from functools import lru_cache
from typing import Generator

import sqlmodel
# from amplitude import Amplitude, BaseEvent
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
# from stytch.api.error import StytchError

from src import crud, models
from src.models.session import sqlmodel_engine
from src.utils import service_logging
# from src.utils.auth import stytch_client
from src.utils.config import settings
from src.utils.service_logging import logger

#amplitude = Amplitude(settings.AMPLITUDE_API_KEY)
# amplitude.configuration.logger.setLevel("ERROR")


# class AmplitudeException(Exception):
#     def __init__(self, message, errors):
#         super().__init__(message)
#         self.errors = errors


def get_db() -> Generator:
    db = None
    try:
        db = sqlmodel.Session(sqlmodel_engine)
        yield db
    finally:
        db.close()


# @lru_cache(maxsize=300)
# def get_stytch_session(session_token: str) -> dict:
#     """
#     Calls the stytch api to authenticate user. Using the session token as
#     the only function argument makes it cacheable.
#
#     :param session_token: A string that is the stytch session token.
#     :return: Dictionary of data from stytch api response.
#     """
#     try:
#         auth_resp = stytch_client.sessions.authenticate(
#             session_token=session_token, session_duration_minutes=525600
#         )
#     except StytchError as err:
#         service_logging.log_stytch_error(err)
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#     return auth_resp.json()
#
#
# def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
#     """
#
#     Authenticates current user based on session token passed in the
#     custom "StytchSessionToken" header and returns the full user model from
#     database.
#
#     :param request: Request
#     :param db: Session
#     :return: UserInDB
#     """
#     session_token_in = request.headers.get("StytchSessionToken")
#     session_data = get_stytch_session(session_token=session_token_in)
#
#     expire_str = session_data["session"]["expires_at"].replace("Z", "")
#     expire_datetime = datetime.datetime.fromisoformat(expire_str)
#
#     stytch_auth_id = session_data["session"]["user_id"]
#     user = crud.user.get_by_auth_id(db, auth_id=stytch_auth_id)
#
#     if session_data["status_code"] != 200 or expire_datetime < datetime.datetime.now():
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#     if not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
#         )
#
#     return user
#
#
# def _track_amplitude_event(
#     request: Request, user: models.User = Depends(get_current_user)
# ):
#     try:
#         headers = request.headers
#         query_string = (
#             request.scope.get("query_string")
#             if request.scope.get("query_string")
#             else "no_query_string"
#         )
#         route = request.scope.get("route")
#         path = route.path
#         route_name = route.name
#         path_params = (
#             request.scope.get("path_params")
#             if request.scope.get("path_params")
#             else "no-path-params"
#         )
#         amplitude.track(
#             BaseEvent(
#                 event_type=route_name,
#                 user_id=user.email,
#                 time=int(datetime.datetime.utcnow().timestamp()),
#                 user_properties={
#                     "user_last_name": user.last_name,
#                     "user_first_name": user.first_name,
#                     "user_role": user.role.role_name,
#                     "user_agent": headers.get("user-agent", "no-user-agent"),
#                 },
#                 event_properties={
#                     "source": "api",
#                     "environment": settings.ENV_NAME,
#                     "http_method": request.scope.get("method", "no_http_method"),
#                     "query_string": query_string,
#                     "path": path,
#                     "path_params": path_params,
#                     "route_name": route_name,
#                     "accept-language": headers.get(
#                         "accept-language", "no-accept-language"
#                     ),
#                 },
#             )
#         )
#     except (AmplitudeException, Exception):
#         logger.exception("amplitude_tracking_event_exception")
#
#
# def track_amplitude_event(
#     request: Request, user: models.User = Depends(get_current_user)
# ):
#     _track_amplitude_event(request, user)
#
#
# class UserRoleAuthorizer:
#     def __init__(self, permission: str):
#         self.permission = permission
#
#     def __call__(self, user: models.User = Depends(get_current_user)):
#         if self.permission not in user.role.permissions:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#         return True
