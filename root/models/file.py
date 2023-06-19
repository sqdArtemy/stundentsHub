import asyncio
import os
from db_init import db
from utilities import delete_file
from sqlalchemy import event
from .mixins import ModelMixinQuerySimplifier


class File(db.Model, ModelMixinQuerySimplifier):
    __tablename__ = "files"

    file_id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(256))
    file_url = db.Column(db.String(256))
    file_format = db.Column(db.String(6))
    file_post_id = db.Column(db.Integer, db.ForeignKey("posts.post_id"))

    def __init__(self, file_name: str, file_url):
        self.file_name = file_name
        self.file_url = file_url
        self.file_format = os.path.splitext(file_name)[1]

    def __repr__(self):
        return self.file_name


@event.listens_for(File, "before_delete")
def delete_file_upon_model_deletion(mapper, connection, target):
    loop = asyncio.get_event_loop()
    print(loop)
    loop.create_task(delete_file(target.file_url[1:]))
