import http_codes
from flask import send_from_directory
from app_init import app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_restful import Resource, reqparse


sort_filter_parser = reqparse.RequestParser()
sort_filter_parser.add_argument("sort_by", type=str, required=False, location="args", action="append")
sort_filter_parser.add_argument("filters", type=str, required=False, location="args")


class RefreshJWTView(Resource):
    @jwt_required(refresh=True)
    def get(self):
        access_token = create_access_token(identity=get_jwt_identity())

        return {"access_token": access_token}, http_codes.HTTP_OK_200


@app.route('/media/uploads/<path:filename>')
@jwt_required()
def serve_media(filename):
    media_folder = app.config["UPLOAD_FOLDER"]
    return send_from_directory(media_folder, filename)
