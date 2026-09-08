from django.contrib import admin
from django.urls import path
from restaurant.views import home


admin.site.site_header = "IDDS Administration"
admin.site.site_title = "IDDS Admin"
admin.site.index_title = "Integrated Digital Dining System"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
]