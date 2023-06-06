from flask import Flask
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

ma = Marshmallow(app)
