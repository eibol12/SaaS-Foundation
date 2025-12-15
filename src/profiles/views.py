from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
@login_required
def profile_view(request, username = None ,*args, **kwargs):
    # profile_user_obj = User.objects.get(username=username)
    profile_user_obj = get_object_or_404(User, username=username)
    return HttpResponse(f"Welcome to your profile {profile_user_obj.username}.")