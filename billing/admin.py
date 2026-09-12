from django.contrib import admin

from .models import Bill, BillItem


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "subtotal",
        "tax",
        "service_charge",
        "total_amount",
        "status",
        "generated_at",
    )

    list_filter = (
        "status",
        "generated_at",
    )

    search_fields = (
        "id",
        "session__customer_name",
        "session__table__table_number",
    )

    readonly_fields = (
        "generated_at",
    )

    inlines = [BillItemInline]


@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = (
        "bill",
        "item_name",
        "quantity",
        "unit_price",
        "total_price",
    )

    search_fields = (
        "item_name",
    )