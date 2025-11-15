from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users import views

app_name = "users"

router = DefaultRouter()
router.register("users", views.UserViewSet)

urlpatterns = [
    # JWT Authentication
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", views.UserRegistrationView.as_view(), name="user-register"),
    # Users CRUD via ViewSet
    path("", include(router.urls)),
]
