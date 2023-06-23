import http_codes
from db_init import redis_store
from flask import request
from flask_jwt_extended import get_jti
from flask_restful import abort
from utilities import is_authorized_error_handler


@is_authorized_error_handler()
def check_blacklisted_tokens():
    jwt_header = request.headers.get("Authorization", None)
    if jwt_header:
        token = jwt_header.split()[1]
        jti = get_jti(encoded_token=token)
        if redis_store.get(jti):
            abort(http_codes.HTTP_UNAUTHORIZED_401, error_message="Your JWT token is revoked.")
