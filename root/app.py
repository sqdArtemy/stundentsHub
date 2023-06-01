from flask import Flask
from flask_cli import FlaskGroup
from flask_restful import Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

db = SQLAlchemy(app)
ma = Marshmallow(app)
parser = reqparse.RequestParser()

migrate = Migrate()
migrate.init_app(app, db)

api = Api(app)
cli = FlaskGroup(app)

# from user import (
#     User, Role, RoleListViewSet, RoleDetailedViewSet, UserListViewSet, UserDetailedViewSet, UserRegisterView
# )
# from university import Faculty, University, UniversityListView, UniversityDetailedView
# from post import Post, Comment

from models import User, Role, University, Faculty, Post, Comment
from views import (
    UserRegisterView, UserDetailedViewSet, UserListViewSet, RoleDetailedViewSet, RoleListViewSet,
    UniversityDetailedView, UniversityListView, FacultyListView, FacultyDetailedView, PostDetailedView, PostListView,
    CommentDetailedView, CommentListView
)

# Role urls
api.add_resource(RoleListViewSet, "/user_roles")
api.add_resource(RoleDetailedViewSet, "/user_role/<int:role_id>")
# User urls
api.add_resource(UserListViewSet, "/users")
api.add_resource(UserDetailedViewSet, "/user/<int:user_id>")
api.add_resource(UserRegisterView, "/register")
# University urls
api.add_resource(UniversityListView, "/universities")
api.add_resource(UniversityDetailedView, "/university/<int:university_id>")
# Faculty urls
api.add_resource(FacultyListView, "/faculties")
api.add_resource(FacultyDetailedView, "/faculty/<int:faculty_id>")
# Post urls
api.add_resource(PostListView, "/posts")
api.add_resource(PostDetailedView, "/post/<int:post_id>")
# Comment urls
api.add_resource(CommentListView, "/comments")
api.add_resource(CommentDetailedView, "/comment/<int:comment_id>")

if __name__ == '__main__':
    cli()
