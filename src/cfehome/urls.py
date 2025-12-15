from django.contrib import admin
from django.urls import path, include
from .views import home_view, about_view, pw_protected_view, user_only_view, staff_only_view
from auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home_view, name="home"),
    path("about/", about_view, name="about"),
    path("login/", auth_views.login_view, name="login"),
    path("register/", auth_views.register_view, name="register"),
    path("accounts/", include("allauth.urls")), #accounts/login/, accounts/register/
    path("protected/", pw_protected_view, name="protected"),
    path("protected/user-only", user_only_view, name="protected_user_only"),
    path("protected/staff-only", staff_only_view, name="protected_staff_only"),
    path("profiles/", include("profiles.urls")),

]
