from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from orders.models import DiningSession, OrderItem
from restaurant.models import DiningTable

from .models import Bill, BillItem


TAX_RATE = Decimal("0.05")
SERVICE_CHARGE_RATE = Decimal("0.10")


def _staff_only(request):
    """
    Billing is available to Admin and Waiter users.
    Chef and Customer users cannot access billing.
    """

    if not request.user.is_authenticated:
        return False

    return (
        request.user.is_superuser
        or request.user.groups.filter(name="Waiter").exists()
    )


@login_required
def billing_dashboard(request):
    """
    Staff billing dashboard.

    Shows active dining sessions that can be billed and
    previously generated bills.
    """

    if not _staff_only(request):
        messages.error(
            request,
            "You do not have permission to access billing.",
        )
        return redirect("home")

    active_sessions = (
        DiningSession.objects
        .filter(status="active")
        .select_related("table")
        .prefetch_related("orders")
        .order_by("-started_at")
    )

    bills = (
        Bill.objects
        .select_related(
            "session",
            "session__table",
        )
        .prefetch_related("items")
        .order_by("-id")
    )

    context = {
        "active_sessions": active_sessions,
        "bills": bills,
    }

    return render(
        request,
        "billing/dashboard.html",
        context,
    )


@login_required
@transaction.atomic
def generate_bill(request, session_id):
    """
    Generate or refresh a bill for a dining session.
    """

    if not _staff_only(request):
        messages.error(
            request,
            "You do not have permission to generate bills.",
        )
        return redirect("home")

    if request.method != "POST":
        return redirect("billing:dashboard")

    session = get_object_or_404(
        DiningSession.objects.select_related("table"),
        id=session_id,
    )

    if session.status != "active":
        messages.warning(
            request,
            "This dining session is no longer active.",
        )

        existing_bill = getattr(session, "bill", None)

        if existing_bill:
            return redirect(
                "billing:bill_detail",
                bill_id=existing_bill.id,
            )

        return redirect("billing:dashboard")

    bill, created = Bill.objects.get_or_create(
        session=session,
    )

    if not created:
        bill.items.all().delete()

    order_items = (
        OrderItem.objects
        .filter(order__session=session)
        .select_related(
            "menu_item",
            "order",
        )
        .order_by("order__created_at", "id")
    )

    subtotal = Decimal("0.00")

    for order_item in order_items:
        quantity = order_item.quantity
        unit_price = order_item.unit_price

        item_total = (
            unit_price
            * Decimal(str(quantity))
        )

        subtotal += item_total

        BillItem.objects.create(
            bill=bill,
            order_item=order_item,
            item_name=order_item.item_name,
            unit_price=unit_price,
            quantity=quantity,
            total_price=item_total,
        )

    tax = (
        subtotal * TAX_RATE
    ).quantize(Decimal("0.01"))

    service_charge = (
        subtotal * SERVICE_CHARGE_RATE
    ).quantize(Decimal("0.01"))

    total_amount = (
        subtotal
        + tax
        + service_charge
    ).quantize(Decimal("0.01"))

    bill.subtotal = subtotal
    bill.tax = tax
    bill.service_charge = service_charge
    bill.total_amount = total_amount
    bill.status = "generated"
    bill.generated_at = timezone.now()

    bill.save(
        update_fields=[
            "subtotal",
            "tax",
            "service_charge",
            "total_amount",
            "status",
            "generated_at",
        ]
    )

    # Put the table into billing state.
    session.table.status = "billing"
    session.table.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        f"Bill #{bill.id} generated successfully.",
    )

    return redirect(
        "billing:bill_detail",
        bill_id=bill.id,
    )


@login_required
def bill_detail(request, bill_id):
    """
    Staff bill detail page.
    """

    if not _staff_only(request):
        messages.error(
            request,
            "You do not have permission to view this bill.",
        )
        return redirect("home")

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


def customer_bill(request):
    """
    Customer-facing bill page.

    Uses the dining session stored in the customer's browser
    session, so customers cannot simply view another table's bill.
    """

    dining_session_id = request.session.get(
        "dining_session_id"
    )

    if not dining_session_id:
        messages.warning(
            request,
            "No active dining session was found.",
        )
        return redirect("table_selection")

    dining_session = get_object_or_404(
        DiningSession.objects.select_related("table"),
        id=dining_session_id,
    )

    bill = get_object_or_404(
        Bill.objects
        .filter(session=dining_session)
        .select_related(
            "session",
            "session__table",
        )
        .prefetch_related("items"),
    )

    return render(
        request,
        "billing/customer_bill.html",
        {
            "bill": bill,
        },
    )


@login_required
def complete_bill(request, bill_id):
    """
    Complete payment and close the dining session.

    The table is returned to AVAILABLE so another customer
    can start a new dining session.
    """

    if not _staff_only(request):
        messages.error(
            request,
            "You do not have permission to complete payments.",
        )
        return redirect("home")

    if request.method != "POST":
        return redirect(
            "billing:bill_detail",
            bill_id=bill_id,
        )

    with transaction.atomic():

        bill = get_object_or_404(
            Bill.objects
            .select_related(
                "session",
                "session__table",
            ),
            id=bill_id,
        )

        session = bill.session
        table = session.table

        bill.status = "completed"
        bill.save(
            update_fields=["status"]
        )

        # Complete all orders belonging to this dining session.
        session.orders.exclude(
            status="cancelled"
        ).update(
            status="completed",
            completed_at=timezone.now(),
        )

        session.status = "completed"
        session.completed_at = timezone.now()

        session.save(
            update_fields=[
                "status",
                "completed_at",
            ]
        )

        table.status = "available"

        table.save(
            update_fields=["status"]
        )

    messages.success(
        request,
        f"Payment completed for Bill #{bill.id}. "
        f"Table {table.table_number} is now available.",
    )

    return redirect(
        "billing:bill_detail",
        bill_id=bill.id,
    )