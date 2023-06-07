from flask_cli import FlaskGroup
from flask_restful import Api
from app_init import app
from flask_jwt_extended import JWTManager
from views import (
    UserRegisterView, UserDetailedViewSet, UserListViewSet, RoleDetailedViewSet, RoleListViewSet,
    UniversityDetailedView, UniversityListView, FacultyListView, FacultyDetailedView, PostDetailedView, PostListView,
    CommentDetailedView, CommentListView, UserLoginView, RefreshJWTView, UserChangePassword, PostRateView, UserMeView
)

JWTManager(app)
api = Api(app)
cli = FlaskGroup(app)

from models import User, Role, University, Faculty, Post, Comment

# Role urls
api.add_resource(RoleListViewSet, "/roles")
api.add_resource(RoleDetailedViewSet, "/role/<int:role_id>")
# User urls
api.add_resource(UserListViewSet, "/users")
api.add_resource(UserDetailedViewSet, "/user/<int:user_id>")
api.add_resource(UserRegisterView, "/user/register")
api.add_resource(UserLoginView, "/user/login")
api.add_resource(UserChangePassword, "/user/change_password")
api.add_resource(UserMeView, "/user/me")
# University urls
api.add_resource(UniversityListView, "/universities")
api.add_resource(UniversityDetailedView, "/university/<int:university_id>")
# Faculty urls
api.add_resource(FacultyListView, "/faculties")
api.add_resource(FacultyDetailedView, "/faculty/<int:faculty_id>")
# Post urls
api.add_resource(PostListView, "/posts")
api.add_resource(PostDetailedView, "/post/<int:post_id>")
api.add_resource(PostRateView, "/post/<int:post_id>/rate")
# Comment urls
api.add_resource(CommentListView, "/comments")
api.add_resource(CommentDetailedView, "/comment/<int:comment_id>")
# Technical urls
api.add_resource(RefreshJWTView, "/token/refresh")

if __name__ == '__main__':
    cli()
