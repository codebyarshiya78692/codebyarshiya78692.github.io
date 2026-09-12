from django.contrib import admin
from django.urls import include, path

from restaurant.views import home


admin.site.site_header = "IDDS Administration"
admin.site.site_title = "IDDS Admin"
admin.site.index_title = "Integrated Digital Dining System"


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Customer home
    path("", home, name="home"),

    # Customer account
    path("", include("accounts.urls")),

    # Restaurant / menu
    path("", include("restaurant.urls")),

    # Cart / orders
    path("", include("orders.urls")),
]