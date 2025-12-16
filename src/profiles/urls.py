from django.urls import path, include
from . import views

urlpatterns = [
    path("<str:username>", views.profile_detail_view, name="profile"),
    path("", views.profile_list_view, name="list"),
]