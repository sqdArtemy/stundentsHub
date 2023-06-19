import json
import http_codes
import asyncio
from db_init import db
from flask_restful import Resource, abort, reqparse
from werkzeug.datastructures import FileStorage
from marshmallow import ValidationError
from flask import jsonify, make_response, request, url_for
from flask_jwt_extended import jwt_required
from models import University
from schemas import UniversityGetSchema, UniversityCreateSchema, UniversityUpdateSchema
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from utilities import is_authorized_error_handler, save_file
from .mixins import PaginationMixin


parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("university_name", location="form")
parser.add_argument("university_email", location="form")
parser.add_argument("university_phone", location="form")
parser.add_argument("university_image", type=FileStorage, location="files")


class UniversityListView(Resource, PaginationMixin):
    universities_get_schema = UniversityGetSchema(many=True)
    university_get_schema = UniversityGetSchema()
    university_create_schema = UniversityCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        universities_query = University.query

        filters = request.args.get("filters")
        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order", "asc")

        try:
            if filters:
                filters_dict = json.loads(filters)
                for key, value in filters_dict.items():
                    universities_query = universities_query.filter(getattr(University, key) == value)

            if sort_by:
                column = getattr(University, sort_by)

                if sort_order.lower() == "desc":
                    column = column.desc()

                universities_query = universities_query.order_by(column)

        except AttributeError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))

        response = self.get_paginated_response(
            query=universities_query,
            items_schema=self.universities_get_schema,
            model_plural_name="universities",
            count_field_name="university_count"
        )

        return response

    @is_authorized_error_handler()
    @jwt_required()
    async def post(self):
        data = parser.parse_args()
        image_file = data["university_image"]

        try:
            with db.session.begin():
                university = self.university_create_schema.load(data)
                db.session.add(university)

                async_tasks = []

                if image_file:
                    db.session.add(university.university_image)
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
        university = University.query.get_or_404(
            university_id, description=OBJECT_DOES_NOT_EXIST.format("University", university_id)
        )

        return jsonify(self.university_get_schema.dump(university))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    async def delete(cls, university_id: int):
        university = University.query.get_or_404(
            university_id, description=OBJECT_DOES_NOT_EXIST.format("University", university_id)
        )
        university.delete()

        return {"success": OBJECT_DELETED.format("University", university_id)}, 200

    @is_authorized_error_handler()
    @jwt_required()
    async def put(self, university_id: int):
        try:
            with db.session.begin():
                university = University.query.get_or_404(
                    university_id, description=OBJECT_DOES_NOT_EXIST.format("University", university_id)
                )

                data = parser.parse_args()
                data = {key: value for key, value in data.items() if value}

                old_image_file = university.university_image
                new_image_file = data.get("university_image")

                updated_university = self.university_update_schema.load(data)

                async_tasks = []

                for key, value in updated_university.items():
                    setattr(university, key, value)

                if new_image_file:
                    if old_image_file:
                        db.session.delete(old_image_file)

                    db.session.add(university.university_image)
                    task = save_file(new_image_file, university.university_image.file_url[1:])
                    async_tasks.append(task)

                await asyncio.gather(*async_tasks)

            return jsonify(self.university_get_schema.dump(university))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))
