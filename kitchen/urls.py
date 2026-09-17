from django.urls import path

from . import views


app_name = "kitchen"


urlpatterns = [

    # ------------------------------------------------------------
    # Kitchen / Chef dashboard
    # ------------------------------------------------------------

    path(
        "",
        views.kitchen_dashboard,
        name="dashboard",
    ),


    # ------------------------------------------------------------
    # Order workflow
    # ------------------------------------------------------------

    path(
        "order/<int:order_id>/accept/",
        views.accept_order,
        name="accept_order",
    ),

    path(
        "order/<int:order_id>/start/",
        views.start_preparing,
        name="start_preparing",
    ),

    path(
        "order/<int:order_id>/ready/",
        views.mark_ready,
        name="mark_ready",
    ),


    # ------------------------------------------------------------
    # Customer service requests
    # ------------------------------------------------------------

    path(
        "service-requests/",
        views.service_requests_dashboard,
        name="service_requests",
    ),

    path(
        "service-requests/<int:request_id>/accept/",
        views.accept_service_request,
        name="accept_service_request",
    ),

    path(
        "service-requests/<int:request_id>/complete/",
        views.complete_service_request,
        name="complete_service_request",
    ),
]