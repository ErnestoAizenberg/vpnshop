from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.ico")),  # Add this
    path("<str:user_id>", views.home_view, name="home"),
    path("api/subscription/<str:user_id>", views.get_subscription, name="subscription"),
]
