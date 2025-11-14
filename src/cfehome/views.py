from django.http import HttpResponse
from django.shortcuts import render
from visits.models import PageVisit


def home_view(request, *args, **kwargs):
    return about_view(request, *args, **kwargs)

def about_view(request, *args, **kwargs):
    path = request.path
    queryset = PageVisit.objects.all()
    page_queryset = PageVisit.objects.filter(path=path)
    try:
        percent = page_queryset.count()/queryset.count() * 100
    except:
        percent = 0

    html_template = "home.html"
    my_title = "This is my title"


    my_context = {
        "page_title": my_title,
        "page_visit_count":page_queryset.count(),
        "page_visit_percentage": percent,
        "total_visit_count":queryset.count(),
    }
    PageVisit.objects.create(path=path)
    return render(request, html_template, my_context)