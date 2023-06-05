import http_codes
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_restful import Resource


class RefreshJWTView(Resource):
    @jwt_required(refresh=True)
    def get(self):
        access_token = create_access_token(identity=get_jwt_identity())

        return {"access_token": access_token}, http_codes.HTTP_OK_200
