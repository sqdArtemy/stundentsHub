from .user import UserRegisterView, UserListViewSet, UserDetailedViewSet, UserLoginView, UserChangePassword,\
    UserMeView, UserFollowView
from .role import RoleDetailedViewSet, RoleListViewSet
from .university import UniversityListView, UniversityDetailedView
from .faculty import FacultyListView, FacultyDetailedView
from .post import PostListView, PostDetailedView, PostRateView, PostAddFile, PostDeleteFile, PostBulkEditFiles
from .comment import CommentListView, CommentDetailedView
from .technical import RefreshJWTView
