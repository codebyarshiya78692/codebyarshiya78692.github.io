from django.urls import path

from . import views


app_name = "billing"


urlpatterns = [
    path(
        "",
        views.billing_dashboard,
        name="dashboard",
    ),

    path(
        "session/<int:session_id>/generate/",
        views.generate_bill,
        name="generate_bill",
    ),

    path(
        "my-bill/",
        views.customer_bill,
        name="customer_bill",
    ),

    path(
        "<int:bill_id>/",
        views.bill_detail,
        name="bill_detail",
    ),

    path(
        "<int:bill_id>/complete/",
        views.complete_bill,
        name="complete_bill",
    ),
]