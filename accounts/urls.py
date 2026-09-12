from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.customer_login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.customer_logout, name="logout"),
]