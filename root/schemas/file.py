import os
import uuid
from flask import url_for
from models import File
from app_init import ma, app
from marshmallow import fields, EXCLUDE, post_load
from db_init import db


class FileSchema(ma.SQLAlchemyAutoSchema):
    file_raw = fields.Raw(type="file", load_only=True, required=True)

    @post_load
    def image_processing(self, data, **kwargs):
        file = data.get("file_raw")
        unique_name = str(uuid.uuid4()) + os.path.splitext(str(file.filename))[1]
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        file.save(save_path)
        file_url = url_for("static", filename=unique_name)

        return File(file.filename, file_url)

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
        fields = ("file_id", "file_name", "file_url")
        sqla_session = db.session
