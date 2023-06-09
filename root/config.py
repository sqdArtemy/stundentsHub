import os
from dotenv.main import load_dotenv


def get_env_variable(name: str) -> (str, Exception):
    try:
        load_dotenv()
        return os.environ[name]
    except KeyError:
        message = f"Expected environment variable {name} was not set."
        return Exception(message)


class Config(object):
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
    UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, "static\\uploads")
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


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
