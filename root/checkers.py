"""
This module contains functions which are used to check conditions
I did it in separate module, because these functions are used throughout whole project
"""
import re
import http_codes
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask import current_app
from flask_restful import abort
from marshmallow import ValidationError


def instance_exists_by_id(_id: int, model) -> bool:
    return model.query.get(_id) is not None


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
    def decorate(function):
        def wrapper(*args, **kwargs):
            try:
                return current_app.ensure_sync(function)(*args, **kwargs)
            except NoAuthorizationError:
                abort(http_codes.HTTP_FORBIDDEN_403, error_message="User is not authorized.")

        return wrapper

    return decorate
