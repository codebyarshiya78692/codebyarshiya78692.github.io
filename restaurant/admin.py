from django.contrib import admin

from .models import (
    DiningTable,
    MenuCategory,
    MenuItem,
)


@admin.register(DiningTable)
class DiningTableAdmin(admin.ModelAdmin):
    list_display = (
        "table_number",
        "capacity",
        "status",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "table_number",
    )


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "is_available",
    )

    list_filter = (
        "category",
        "is_available",
    )

    search_fields = (
        "name",
        "description",
    )

    fieldsets = (
        (
            "Menu Item Details",
            {
                "fields": (
                    "category",
                    "name",
                    "description",
                    "price",
                    "is_available",
                ),
            },
        ),
        (
            "Food Image",
            {
                "fields": (
                    "image",
                ),
                "description": (
                    "Upload the actual food image that "
                    "will appear on the customer menu."
                ),
            },
        ),
    )