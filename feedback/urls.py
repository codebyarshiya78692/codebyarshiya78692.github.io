from django.urls import path

from . import views


app_name = "feedback"


urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "session/<int:session_id>/",
        views.create_feedback,
        name="create",
    ),
]