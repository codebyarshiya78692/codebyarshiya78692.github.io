from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [

    # ========================================================
    # UNIFIED LOGIN
    # ========================================================

    path(
        "login/",
        views.customer_login,
        name="login",
    ),

    path(
        "logout/",
        views.customer_logout,
        name="logout",
    ),

    # ========================================================
    # CUSTOMER
    # ========================================================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),

    # ========================================================
    # LEGACY ROLE LOGIN URLS
    #
    # These now use the SAME login page so there is only
    # one real login experience.
    # ========================================================

    path(
        "chef/login/",
        views.customer_login,
        name="chef_login",
    ),

    path(
        "waiter/login/",
        views.customer_login,
        name="waiter_login",
    ),

    # ========================================================
    # WAITER
    # ========================================================

    path(
        "waiter/",
        views.waiter_dashboard,
        name="waiter_dashboard",
    ),

    path(
        "waiter/request/<int:request_id>/accept/",
        views.waiter_accept_request,
        name="waiter_accept_request",
    ),

    path(
        "waiter/request/<int:request_id>/complete/",
        views.waiter_complete_request,
        name="waiter_complete_request",
    ),

    path(
        "waiter/order/<int:order_id>/serve/",
        views.waiter_serve_order,
        name="waiter_serve_order",
    ),

    # ========================================================
    # STAFF
    # ========================================================

    path(
        "staff/",
        views.staff_dashboard,
        name="staff_dashboard",
    ),
]