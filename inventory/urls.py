from django.urls import path

from . import views


app_name = "inventory"


urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "ingredient/<int:ingredient_id>/add-stock/",
        views.add_stock,
        name="add_stock",
    ),

    path(
        "ingredient/<int:ingredient_id>/adjust/",
        views.adjust_stock,
        name="adjust_stock",
    ),

    path(
        "ingredient/<int:ingredient_id>/use/",
        views.use_stock,
        name="use_stock",
    ),

    path(
        "ingredient/<int:ingredient_id>/waste/",
        views.record_waste,
        name="record_waste",
    ),

    path(
        "ingredient/<int:ingredient_id>/return/",
        views.return_stock,
        name="return_stock",
    ),

    path(
        "ingredient/<int:ingredient_id>/history/",
        views.stock_movement_history,
        name="movement_history",
    ),
]