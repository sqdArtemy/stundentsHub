from flask import Flask
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

ma = Marshmallow(app)
mail = Mail(app)
socketio = SocketIO(app, cors_allowed_origins="*")
