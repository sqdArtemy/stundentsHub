from .app import app, db, parser, ma
from .checkers import instance_exists
from .config import DevelopmentConfig, ProductionConfig
from .text_templates import *
import user, post, university
import models, views, schemas
