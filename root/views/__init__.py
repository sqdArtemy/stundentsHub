from .user import UserRegisterView, UserListViewSet, UserDetailedViewSet, UserLoginView, UserChangePassword,\
    UserMeView, UserFollowView, UserLogOutView
from .role import RoleDetailedViewSet, RoleListViewSet
from .university import UniversityListView, UniversityDetailedView
from .faculty import FacultyListView, FacultyDetailedView
from .post import PostListView, PostDetailedView, PostRateView, PostAddFile, PostDeleteFile, PostBulkEditFiles
from .comment import CommentListView, CommentDetailedView
from .technical import RefreshJWTView
from .notification import NotificationListView, NotificationDetailedView
from .message import MessageListView, MessageDetailedView
