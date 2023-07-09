import re
import os

import aiofiles
from app_init import app
import http_codes
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt.exceptions import ExpiredSignatureError
from flask import current_app
from flask_restful import abort
from marshmallow import ValidationError
from exceptions import JWTRevokedError


async def save_file(file, file_url):
    save_path = os.path.join(app.config["ROOT_FOLDER"], file_url)
    print(save_path)
    async with aiofiles.open(save_path, "wb") as f:
        await f.write(file.read())


async def delete_file(file_url):
    file_path = os.path.join(app.config["ROOT_FOLDER"], file_url)
    if os.path.exists(file_path):
        os.remove(file_path)


def instance_exists_by_id(_id: int, model) -> bool:
    return model.query.get(_id) is not None


def is_password_valid(password: str):
    requirements = {
        "length": (len(password) >= 8, "Password should have a minimum length of 8 characters."),
        "uppercase": (re.search(r"[A-Z]", password), "Password should contain at least one uppercase letter."),
        "lowercase": (re.search(r"[a-z]", password), "Password should contain at least one lowercase letter."),
        "digit": (re.search(r"\d", password), "Password should contain at least one digit."),
        "special_character": (re.search(r"[@$!%*?&]", password),
                              "Password should contain at least one special character from the set [@ $ ! % * ? &].")
    }

    warnings = {key: message for key, (condition, message) in requirements.items() if not condition}

    if warnings:
        raise ValidationError(warnings)

    return {"success": "Password is strong and meets all the criteria."}


def is_email_valid(email: str):
    email_regexp = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
    if not re.match(email_regexp, email):
        raise ValidationError("Entered email is invalid.")


def is_phone_valid(phone: str):
    phone_regexp = r"^\+[\d]+$"
    if not re.match(phone_regexp, phone):
        raise ValidationError("Entered phone number is invalid")


def is_name_valid(name: str):
    name_regexp = r"^[a-zA-Z_ ]+([\\s-][a-zA-Z_ ]+)*$"
    if not re.match(name_regexp, name):
        raise ValidationError('Field should consist only of letters, spaces or dashes.')


def is_date_valid(date: str):
    date_regexp = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_regexp, date):
        raise ValidationError("Entered date has invalid format.")


def is_datetime_valid(datetime: str):
    datetime_regexp = r"^(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2})\.(\d{6})$"
    if not re.match(datetime_regexp, datetime):
        raise ValidationError("Entered date and time has invalid format.")


# Changes the warning message if user is not authorized
def is_authorized_error_handler():
    error_mappings = {
        NoAuthorizationError: http_codes.HTTP_UNAUTHORIZED_401,
        ExpiredSignatureError: http_codes.HTTP_NOT_ACCEPTABLE_406,
        JWTRevokedError: http_codes.HTTP_UNAUTHORIZED_401
    }

    def decorate(function):
        def wrapper(*args, **kwargs):
            try:
                return current_app.ensure_sync(function)(*args, **kwargs)
            except (NoAuthorizationError, ExpiredSignatureError, JWTRevokedError) as e:
                if type(e) in error_mappings.keys():
                    status_code = error_mappings[type(e)]
                    abort(status_code, error_message=str(e))

        return wrapper

    return decorate
