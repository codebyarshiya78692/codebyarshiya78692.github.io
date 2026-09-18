from django.contrib import admin, messages

from .models import (
    DiningTable,
    MenuCategory,
    MenuItem,
)
from .services import release_table


@admin.action(description="Release selected tables safely")
def release_selected_tables(modeladmin, request, queryset):
    """
    Safely release selected dining tables.

    Tables with an active DiningSession are NOT released.
    """

    released = 0
    blocked = 0

    for table in queryset:
        success, message = release_table(table.id)

        if success:
            released += 1
        else:
            blocked += 1

            modeladmin.message_user(
                request,
                message,
                level=messages.WARNING,
            )

    if released:
        modeladmin.message_user(
            request,
            f"{released} table(s) released and marked Available.",
            level=messages.SUCCESS,
        )

    if blocked:
        modeladmin.message_user(
            request,
            (
                f"{blocked} table(s) were not released because "
                "they still have an active dining session."
            ),
            level=messages.WARNING,
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

    actions = [
        release_selected_tables,
    ]


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