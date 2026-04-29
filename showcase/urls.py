from django.urls import path

from . import views

app_name = "showcase"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/ionicons/", views.ionicons_search, name="ionicons_search"),
]
