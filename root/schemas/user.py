from marshmallow import fields, validate, post_load, validates, ValidationError, EXCLUDE, pre_load
from werkzeug.security import generate_password_hash
from models import User, Role, Faculty, University
from app_init import ma
from .file import FileCreateSchema, FileGetSchema
from .university import UniversityGetSchema
from .role import RoleGetSchema
from .faculty import FacultyGetSchema
from utilities import is_email_valid, instance_exists_by_id, is_phone_valid, is_name_valid, is_password_valid
from db_init import db


class UserSchemaMixin:
    user_tg_link = fields.Str(required=False, allow_none=True)
    user_phone = fields.Str(required=False, allow_none=True, validate=is_phone_valid)
    user_image = fields.Nested(FileCreateSchema(), allow_none=True)

    @pre_load
    def serialize_data(self, data, **kwargs):
        image_file = data.get("user_image")
        if image_file:
            data["user_image"] = {"file_raw": image_file}

        return data

    @validates("user_email")
    def validate_user_email(self, value):
        if len(User.query.filter_by(user_email=value).all()):
            raise ValidationError("User with this email already exists!")

    @validates("user_phone")
    def validate_user_phone(self, value):
        if value and len(User.query.filter_by(user_phone=value).all()):
            raise ValidationError("User with this phone already exists!")

    @validates("user_role")
    def validate_user_role(self, value):
        if not instance_exists_by_id(_id=value, model=Role):
            raise ValidationError(f"Role with role_id = {value} does not exist.")

    @validates("user_university")
    def validate_user_university(self, value):
        if not instance_exists_by_id(_id=value, model=University):
            raise ValidationError(f"University with university_id = {value} does not exist.")

    @validates("user_faculty")
    def validate_user_faculty(self, value):
        if not instance_exists_by_id(_id=value, model=Faculty):
            raise ValidationError(f"Faculty with faculty_id = {value} does not exist.")

    @post_load
    def create_user_password_hash(self, data, **kwargs):
        if data.get("user_password"):
            data["user_password"] = generate_password_hash(data["user_password"])

        return data


class UserGetSchema(ma.SQLAlchemyAutoSchema):
    user_image = fields.Nested(FileGetSchema())
    university = fields.Nested(UniversityGetSchema(only=("university_id", "university_name")),
                               data_key="user_university")
    faculty = fields.Nested(FacultyGetSchema(only=("faculty_id", "faculty_name")), data_key="user_faculty")
    role = fields.Nested(RoleGetSchema(only=("role_id", "role_name")), data_key="user_role")

    class Meta:
        model = User
        ordered = True
        fields = ("user_id", "user_name", "user_surname", "user_email", "user_card_id",
                  "user_birthday", "user_image", "role", "faculty", "university", "user_enrolment_year",
                  "user_tg_link", "user_phone", "user_followers", "user_following", "user_liked_posts",
                  "user_disliked_posts")
        include_relationships = True
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session


class UserCreateSchema(ma.SQLAlchemyAutoSchema, UserSchemaMixin):
    user_name = fields.Str(required=True, validate=is_name_valid)
    user_surname = fields.Str(required=True, validate=is_name_valid)
    user_email = fields.Email(required=True, validate=is_email_valid)
    user_password = fields.Str(required=True, validate=is_password_valid)
    user_card_id = fields.Str(required=True)
    user_birthday = fields.Date(required=True, format="%Y-%m-%d")
    user_role = fields.Integer(required=True)
    user_faculty = fields.Integer(required=True)
    user_university = fields.Integer(required=True)
    user_enrolment_year = fields.Date(required=True, format="%Y-%m-%d")

    class Meta:
        model = User
        fields = ("user_name", "user_surname", "user_email", "user_password", "user_card_id",
                  "user_birthday", "user_image", "user_role", "user_faculty", "user_university", "user_enrolment_year",
                  "user_tg_link", "user_phone")
        unknown = EXCLUDE
        include_relationships = True
        load_instance = True


class UserUpdateSchema(ma.SQLAlchemyAutoSchema, UserSchemaMixin):
    user_name = fields.Str(required=False, validate=is_name_valid)
    user_surname = fields.Str(required=False, validate=is_name_valid)
    user_email = fields.Email(required=False, validate=is_email_valid)
    user_password = fields.Str(required=False, validate=is_password_valid)
    user_card_id = fields.Str(required=False)
    user_birthday = fields.Date(required=False, format="%Y-%m-%d")
    user_role = fields.Integer(required=False)
    user_faculty = fields.Integer(required=False)
    user_university = fields.Integer(required=False)
    user_enrolment_year = fields.Date(required=False, format="%Y-%m-%d")

    class Meta:
        model = User
        fields = ("user_name", "user_surname", "user_email", "user_password", "user_card_id",
                  "user_birthday", "user_image", "user_role", "user_faculty", "user_university", "user_enrolment_year",
                  "user_tg_link", "user_phone")
        include_relationships = True
        load_instance = False
        unknown = EXCLUDE
