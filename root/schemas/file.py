import os
import uuid
from werkzeug.utils import secure_filename
from flask import url_for
from models import File
from app_init import ma
from marshmallow import fields, EXCLUDE, post_load
from db_init import db


class FileCreateSchema(ma.SQLAlchemyAutoSchema):
    file_raw = fields.Raw(type="file", load_only=True, required=True)

    @post_load
    def image_processing(self, data, **kwargs):
        file = data.get("file_raw")
        file_name = secure_filename(file.filename)
        unique_name = str(uuid.uuid4()) + os.path.splitext(file_name)[1]
        file_url = url_for("serve_media", filename=f"{unique_name}")

        return File(file_name, file_url)

    class Meta:
        model = File
        ordered = True
        load_instance = False
        fields = ("file_id", "file_name", "file_url", "file_raw")
        sqla_session = db.session
        unknown = EXCLUDE


class FileGetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = File
        ordered = True
        load_instance = True
        fields = ("file_id", "file_name", "file_url", "file_raw")
        sqla_session = db.session
