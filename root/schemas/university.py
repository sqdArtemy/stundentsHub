from marshmallow import fields, validates, ValidationError, EXCLUDE, pre_load
from models import University
from .faculty import FacultyGetSchema
from .file import FileGetSchema, FileCreateSchema
from app_init import ma
from utilities import is_name_valid, is_email_valid, is_phone_valid


class UniversitySchemaMixin:
    university_image = fields.Nested(FileCreateSchema(), allow_none=True)

    @pre_load
    def serialize_data(self, data, **kwargs):
        image_file = data.get("university_image")
        if image_file:
            data["university_image"] = {"file_raw": image_file}

        return data

    @validates("university_email")
    def validate_university_email(self, value):
        if University.query.filter_by(university_email=value).first() is not None:
            raise ValidationError("University with this email is already exists.")


class UniversityGetSchema(ma.SQLAlchemyAutoSchema):
    university_faculties = fields.Nested(FacultyGetSchema(), many=True)
    university_image = fields.Nested(FileGetSchema())

    class Meta:
        ordered = True
        model = University
        fields = ("university_id", "university_name", "university_image", "university_email", "university_phone",
                  "university_faculties")
        include_relationships = True
        load_instance = True
        unknown = EXCLUDE


class UniversityUpdateSchema(ma.SQLAlchemyAutoSchema, UniversitySchemaMixin):
    university_name = fields.Str(required=False, validate=is_name_valid)
    university_email = fields.Email(required=False, validate=is_email_valid)
    university_phone = fields.Str(required=False, validate=is_phone_valid)

    class Meta:
        ordered = True
        model = University
        fields = ("university_name", "university_email", "university_phone", "university_image")
        include_relationships = True
        include_fk = True
        unknown = EXCLUDE


class UniversityCreateSchema(ma.SQLAlchemyAutoSchema, UniversitySchemaMixin):
    university_name = fields.Str(required=True, validate=is_name_valid)
    university_email = fields.Email(required=True, validate=is_email_valid)
    university_phone = fields.Str(required=True, validate=is_phone_valid)

    class Meta:
        model = University
        ordered = True
        fields = ("university_name", "university_email", "university_phone", "university_image")
        load_instance = True
        include_relationships = True
        unknown = EXCLUDE
