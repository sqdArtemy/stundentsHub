import http_codes
import asyncio
from flask_restful import Resource, abort, reqparse
from werkzeug.datastructures import FileStorage
from marshmallow import ValidationError
from flask import jsonify, make_response
from flask_jwt_extended import jwt_required
from models import University
from schemas import UniversityGetSchema, UniversityCreateSchema, UniversityUpdateSchema
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from utilities import is_authorized_error_handler, save_file, delete_file

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("university_name", location="form")
parser.add_argument("university_email", location="form")
parser.add_argument("university_phone", location="form")
parser.add_argument("university_image", type=FileStorage, location="files")


class UniversityListView(Resource):
    universities_get_schema = UniversityGetSchema(many=True)
    university_get_schema = UniversityGetSchema()
    university_create_schema = UniversityCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        universities = University.query.all()
        return jsonify(self.universities_get_schema.dump(universities))

    @is_authorized_error_handler()
    @jwt_required()
    async def post(self):
        data = parser.parse_args()
        image_file = data["university_image"]

        try:
            university = self.university_create_schema.load(data)
            university.create()

            async_tasks = []

            if image_file:
                university.university_image.create()
                task = save_file(image_file, university.university_image.file_url[1:])
                async_tasks.append(task)

            await asyncio.gather(*async_tasks)

            return make_response(jsonify(self.university_get_schema.dump(university)), http_codes.HTTP_CREATED_201)
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class UniversityDetailedView(Resource):
    university_get_schema = UniversityGetSchema()
    university_update_schema = UniversityUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, university_id: int):
        university = University.query.get(university_id)
        if not university:
            abort(http_codes.HTTP_NOT_FOUND_404,
                  error_message=OBJECT_DOES_NOT_EXIST.format("University", university_id))

        return jsonify(self.university_get_schema.dump(university))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, university_id: int):
        university = University.query.get(university_id)
        if not university:
            abort(http_codes.HTTP_NOT_FOUND_404,
                  error_message=OBJECT_DOES_NOT_EXIST.format("University", university_id))
        university.delete()

        return {"success": OBJECT_DELETED.format("University", university_id)}, 200

    @is_authorized_error_handler()
    @jwt_required()
    async def put(self, university_id: int):
        university = University.query.get(university_id)
        if not university:
            abort(http_codes.HTTP_NOT_FOUND_404,
                  error_message=OBJECT_DOES_NOT_EXIST.format("University", university_id))

        data = parser.parse_args()
        data = {key: value for key, value in data.items() if value}

        old_image_file = university.university_image
        new_image_file = data.get("university_image")

        try:
            updated_university = self.university_update_schema.load(data)

            async_tasks = []

            for key, value in updated_university.items():
                setattr(university, key, value)

            if new_image_file:
                if old_image_file:
                    task = delete_file(old_image_file.file_url[1:])
                    async_tasks.append(task)
                    old_image_file.delete()

                university.university_image.create()
                task = save_file(new_image_file, university.university_image.file_url[1:])
                async_tasks.append(task)

            university.save_changes()
            await asyncio.gather(*async_tasks)

            return jsonify(self.university_get_schema.dump(university))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))
