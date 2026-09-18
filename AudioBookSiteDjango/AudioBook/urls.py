from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("news", views.news, name="news"),
    path("author/<int:id>", views.author),
    path("cycle/<int:id>", views.cycle),
]
