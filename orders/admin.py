from django.contrib import admin

from .models import (
    DiningSession,
    Order,
    OrderItem,
    ServiceRequest,
)


@admin.register(DiningSession)
class DiningSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "table",
        "customer_name",
        "status",
        "started_at",
    )

    list_filter = (
        "status",
        "started_at",
    )

    search_fields = (
        "customer_name",
        "table__table_number",
        "session_token",
    )

    readonly_fields = (
        "session_token",
        "started_at",
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "item_name",
        "unit_price",
        "total_price",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "status",
        "created_at",
        "total_amount",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "id",
        "session__customer_name",
        "session__table__table_number",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "accepted_at",
        "preparing_at",
        "ready_at",
        "served_at",
        "completed_at",
        "total_amount",
    )

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "item_name",
        "quantity",
        "unit_price",
        "total_price",
    )

    search_fields = (
        "item_name",
        "order__id",
    )

    readonly_fields = (
        "item_name",
        "unit_price",
        "total_price",
    )


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "request_type",
        "status",
        "requested_at",
    )

    list_filter = (
        "request_type",
        "status",
        "requested_at",
    )

    search_fields = (
        "message",
        "session__customer_name",
        "session__table__table_number",
    )

    readonly_fields = (
        "requested_at",
    )