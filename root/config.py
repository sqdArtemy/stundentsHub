import os
from dotenv.main import load_dotenv
from exceptions import EnvVariableError

load_dotenv()


def get_env_variable(name: str) -> (str, Exception):
    try:
        return os.environ[name]
    except KeyError:
        message = f"Expected environment variable {name} was not set."
        return EnvVariableError(message)


class Config:
    # App settings
    TESTING = False
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = get_env_variable("SECRET_KEY")
    JWT_SECRET_KEY = get_env_variable("JWT_SECRET_KEY")
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JSON_SORT_KEYS = False
    ROOT_FOLDER = os.path.abspath(os.path.dirname(__name__))
    UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, "media/uploads")
    #  Postgres config
    POSTGRES_URL = get_env_variable("POSTGRES_URL")
    POSTGRES_USER = get_env_variable("POSTGRES_USER")
    POSTGRES_PW = get_env_variable("POSTGRES_PW")
    POSTGRES_DB = get_env_variable("POSTGRES_DB")
    # Database URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_URL}/{POSTGRES_DB}"
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
    # Redis
    REDIS_HOST = get_env_variable("REDIS_HOST")
    REDIS_PORT = get_env_variable("REDIS_PORT")
    REDIS_DB = get_env_variable("REDIS_DB")
    # Email
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = get_env_variable("MAIL_USERNAME")
    MAIL_PASSWORD = get_env_variable("MAIL_PASSWORD")
    # Celery
    CELERY_BROKER_URL = get_env_variable("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = get_env_variable("CELERY_RESULT_BACKEND")
    CELERY_INCLUDE = ["tasks"]


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
