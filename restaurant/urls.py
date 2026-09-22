from django.urls import path

from . import table_views, views, service_views


app_name = "restaurant"


urlpatterns = [
    # ============================================================
    # MENU
    # ============================================================

    path(
        "menu/",
        views.menu,
        name="menu",
    ),

    # ============================================================
    # TABLE MANAGEMENT
    # ============================================================

    path(
        "tables/<int:table_id>/release/",
        table_views.release_table_view,
        name="release_table",
    ),

    # ============================================================
    # CUSTOMER SERVICE REQUESTS
    # ============================================================

    path(
        "service-requests/",
        service_views.service_requests,
        name="service_requests",
    ),

    path(
        "service-requests/create/",
        service_views.create_service_request,
        name="create_service_request",
    ),

    # ============================================================
    # STAFF SERVICE REQUESTS
    # ============================================================

    path(
        "service-requests/staff/",
        service_views.staff_service_requests,
        name="staff_service_requests",
    ),

    path(
        "service-requests/staff/<int:request_id>/",
        service_views.staff_service_request_detail,
        name="staff_service_request_detail",
    ),

    path(
        "service-requests/staff/<int:request_id>/accept/",
        service_views.accept_service_request,
        name="accept_service_request",
    ),

    path(
        "service-requests/staff/<int:request_id>/complete/",
        service_views.complete_service_request,
        name="complete_service_request",
    ),
]