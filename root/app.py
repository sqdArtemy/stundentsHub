import http_codes
from flask_cli import FlaskGroup
from flask_restful import Api, request, abort
from app_init import app
from db_init import redis_store
from flask_jwt_extended import JWTManager, get_jti
from views import (
    UserRegisterView, UserDetailedViewSet, UserListViewSet, RoleDetailedViewSet, RoleListViewSet,
    UniversityDetailedView, UniversityListView, FacultyListView, FacultyDetailedView, PostDetailedView, PostListView,
    CommentDetailedView, CommentListView, UserLoginView, RefreshJWTView, UserChangePassword, PostRateView, UserMeView,
    UserFollowView, PostAddFile, PostDeleteFile, PostBulkEditFiles, NotificationListView, NotificationDetailedView,
    UserLogOutView
)

JWTManager(app)
api = Api(app)
cli = FlaskGroup(app)

from models import User, Role, University, Faculty, Post, Comment, File, Notification

# Role urls
api.add_resource(RoleListViewSet, "/roles")
api.add_resource(RoleDetailedViewSet, "/role/<int:role_id>")
# User urls
api.add_resource(UserListViewSet, "/users")
api.add_resource(UserDetailedViewSet, "/user/<int:user_id>")
api.add_resource(UserRegisterView, "/user/register")
api.add_resource(UserLoginView, "/user/login")
api.add_resource(UserLogOutView, "/user/logout")
api.add_resource(UserChangePassword, "/user/change_password")
api.add_resource(UserMeView, "/user/me")
api.add_resource(UserFollowView, "/user/<int:user_id>/follow")
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
api.add_resource(PostAddFile, "/post/<int:post_id>/file")
api.add_resource(PostDeleteFile, "/post/<int:post_id>/file/<int:file_id>")
api.add_resource(PostBulkEditFiles, "/post/<int:post_id>/files")
# Comment urls
api.add_resource(CommentListView, "/comments")
api.add_resource(CommentDetailedView, "/comment/<int:comment_id>")
# Notification urls
api.add_resource(NotificationListView, "/notifications")
api.add_resource(NotificationDetailedView, "/notification/<int:notification_id>")
# Technical urls
api.add_resource(RefreshJWTView, "/token/refresh")


@app.before_request
def check_blacklisted_tokens():
    jwt_header = request.headers.get("Authorization", None)
    if jwt_header:
        token = jwt_header.split()[1]
        jti = get_jti(encoded_token=token)
        if redis_store.get(jti):
            abort(http_codes.HTTP_UNAUTHORIZED_401, error_message="Your JWT token is revoked.")


if __name__ == '__main__':
    cli()
