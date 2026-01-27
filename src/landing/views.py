from django.shortcuts import render
from visits.models import PageVisit
from helpers.numbers import shorten_number
from dashboard.views import dashboard_view

# Create your views here.
def landing_dashboard_page_view(request):
    if request.user.is_authenticated:
        return dashboard_view(request)
    path = request.path
    queryset = PageVisit.objects.all()
    PageVisit.objects.create(path=path)
    page_views_formatted = shorten_number(queryset.count())
    context = {
        "page_view_count":page_views_formatted
    }
    return render(request, 'landing/main.html', context)