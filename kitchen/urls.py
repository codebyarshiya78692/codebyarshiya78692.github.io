from django.urls import path

from . import views


app_name = "kitchen"


urlpatterns = [

    # Kitchen / Chef dashboard
    path(
        "",
        views.kitchen_dashboard,
        name="dashboard",
    ),

    # Accept a new order
    path(
        "order/<int:order_id>/accept/",
        views.accept_order,
        name="accept_order",
    ),

    # Start preparing an accepted order
    path(
        "order/<int:order_id>/start/",
        views.start_preparing,
        name="start_preparing",
    ),

    # Mark a prepared order as ready
    path(
        "order/<int:order_id>/ready/",
        views.mark_ready,
        name="mark_ready",
    ),
]