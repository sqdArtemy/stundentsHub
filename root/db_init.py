import redis
from app_init import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Main database
db = SQLAlchemy(app)
migrate = Migrate()
migrate.init_app(app, db)

# Redis set-up
redis_store = redis.Redis(
    host=app.config["REDIS_HOST"],
    port=app.config["REDIS_PORT"],
    db=app.config["REDIS_DB"]
)
