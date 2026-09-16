from django.contrib import admin


# Orders are managed by orders.admin.
#
# Do not register Order here.
# Registering Order in both kitchen.admin and orders.admin
# causes Django's AlreadyRegistered error.
#
# The kitchen application uses the custom Kitchen Dashboard
# instead of duplicating the Order model in Django Admin.