from django.urls import path

from . import table_views, views


app_name = "restaurant"


urlpatterns = [
    path(
        "menu/",
        views.menu,
        name="menu",
    ),

    path(
        "tables/<int:table_id>/release/",
        table_views.release_table_view,
        name="release_table",
    ),
]