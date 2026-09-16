from django.contrib import admin

from .models import Ingredient, StockMovement


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "unit",
        "current_stock",
        "reorder_level",
        "is_active",
    )

    list_filter = (
        "unit",
        "is_active",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "ingredient",
        "movement_type",
        "quantity",
        "created_at",
    )

    list_filter = (
        "movement_type",
        "created_at",
    )

    search_fields = (
        "ingredient__name",
        "notes",
    )

    ordering = (
        "-created_at",
    )