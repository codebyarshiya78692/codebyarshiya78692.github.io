from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from orders.models import DiningSession, OrderItem

from .models import Bill, BillItem


TAX_RATE = Decimal("0.05")
SERVICE_CHARGE_RATE = Decimal("0.10")


def billing_dashboard(request):
    """
    Billing dashboard.

    Shows dining sessions and existing bills.
    """

    sessions = (
        DiningSession.objects
        .select_related("table")
        .prefetch_related("orders")
        .order_by("-id")
    )

    bills = (
        Bill.objects
        .select_related("session", "session__table")
        .prefetch_related("items")
        .order_by("-id")
    )

    context = {
        "sessions": sessions,
        "bills": bills,
    }

    return render(
        request,
        "billing/dashboard.html",
        context,
    )


def generate_bill(request, session_id):
    """
    Generate a bill for a dining session.
    """

    session = get_object_or_404(
        DiningSession.objects.select_related("table"),
        id=session_id,
    )

    bill, created = Bill.objects.get_or_create(
        session=session,
    )

    if not created:
        bill.items.all().delete()

    order_items = (
        OrderItem.objects
        .filter(order__session=session)
        .select_related("menu_item", "order")
    )

    subtotal = Decimal("0.00")

    for order_item in order_items:
        quantity = getattr(order_item, "quantity", 1)

        unit_price = getattr(
            order_item,
            "unit_price",
            getattr(
                order_item,
                "price",
                Decimal("0.00"),
            ),
        )

        item_total = (
            Decimal(str(unit_price))
            * Decimal(str(quantity))
        )

        subtotal += item_total

        BillItem.objects.create(
            bill=bill,
            order_item=order_item,
            item_name=str(
                getattr(
                    order_item,
                    "menu_item",
                    getattr(
                        order_item,
                        "item",
                        "Item",
                    ),
                )
            ),
            unit_price=unit_price,
            quantity=quantity,
            total_price=item_total,
        )

    tax = subtotal * TAX_RATE
    service_charge = subtotal * SERVICE_CHARGE_RATE
    total_amount = (
        subtotal
        + tax
        + service_charge
    )

    bill.subtotal = subtotal
    bill.tax = tax
    bill.service_charge = service_charge
    bill.total_amount = total_amount
    bill.status = "generated"
    bill.generated_at = timezone.now()
    bill.save()

    messages.success(
        request,
        f"Bill #{bill.id} generated successfully.",
    )

    return redirect(
        "billing:bill_detail",
        bill_id=bill.id,
    )


def bill_detail(request, bill_id):
    """
    Display a complete bill.
    """

    bill = get_object_or_404(
        Bill.objects
        .select_related(
            "session",
            "session__table",
        )
        .prefetch_related("items"),
        id=bill_id,
    )

    return render(
        request,
        "billing/detail.html",
        {
            "bill": bill,
        },
    )


def complete_bill(request, bill_id):
    """
    Mark a bill as completed.
    """

    bill = get_object_or_404(
        Bill,
        id=bill_id,
    )

    bill.status = "completed"
    bill.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        f"Bill #{bill.id} marked as completed.",
    )

    return redirect(
        "billing:bill_detail",
        bill_id=bill.id,
    )