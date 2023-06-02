from flask import Flask
from flask_marshmallow import Marshmallow
from flask_restful import reqparse

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

ma = Marshmallow(app)
parser = reqparse.RequestParser()
