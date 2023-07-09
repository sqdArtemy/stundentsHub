from flask import Flask
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO
from flask_mail import Mail
from celery import Celery

app = Flask(__name__)
app.app_context().push()
app.config.from_object("config.DevelopmentConfig")

ma = Marshmallow(app)
mail = Mail(app)
socketio = SocketIO(app, cors_allowed_origins="*")
celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)
