from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from orders.models import Order


# ============================================================
# STAFF ACCESS
# ============================================================

def _staff_only(request):
    """
    Kitchen is an internal staff area.

    For the current project sprint, any authenticated staff
    account can access the kitchen dashboard. Later we can
    tighten this to a dedicated Chef group without changing
    the order workflow.
    """

    if not request.user.is_authenticated:
        return False

    return request.user.is_staff


# ============================================================
# KITCHEN DASHBOARD
# ============================================================

@login_required
def kitchen_dashboard(request):
    """
    Main chef dashboard.

    Shows all active kitchen orders:
        new
        accepted
        preparing
        ready

    Orders are displayed with newest orders first.
    """

    if not _staff_only(request):
        messages.error(
            request,
            "Kitchen access is restricted to staff members.",
        )
        return redirect("home")

    orders = (
        Order.objects
        .filter(
            status__in=[
                "new",
                "accepted",
                "preparing",
                "ready",
            ]
        )
        .select_related(
            "session",
            "session__table",
        )
        .prefetch_related(
            "items",
        )
        .order_by(
            "created_at"
        )
    )

    new_orders = orders.filter(
        status="new"
    )

    accepted_orders = orders.filter(
        status="accepted"
    )

    preparing_orders = orders.filter(
        status="preparing"
    )

    ready_orders = orders.filter(
        status="ready"
    )

    return render(
        request,
        "kitchen/dashboard.html",
        {
            "orders": orders,
            "new_orders": new_orders,
            "accepted_orders": accepted_orders,
            "preparing_orders": preparing_orders,
            "ready_orders": ready_orders,
        },
    )


# ============================================================
# ACCEPT ORDER
# ============================================================

@login_required
def accept_order(request, order_id):
    """
    Chef accepts a newly received order.
    """

    if not _staff_only(request):
        messages.error(
            request,
            "Kitchen access is restricted to staff members.",
        )
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen:dashboard")

    order = get_object_or_404(
        Order.objects.select_related(
            "session",
            "session__table",
        ),
        id=order_id,
    )

    if order.status != "new":
        messages.warning(
            request,
            f"Order #{order.id} is already {order.get_status_display().lower()}.",
        )
        return redirect("kitchen:dashboard")

    order.status = "accepted"
    order.accepted_at = timezone.now()
    order.save(
        update_fields=[
            "status",
            "accepted_at",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Order #{order.id} has been accepted by the kitchen.",
    )

    return redirect("kitchen:dashboard")


# ============================================================
# START PREPARING
# ============================================================

@login_required
def start_preparing(request, order_id):
    """
    Move an accepted order into preparation.
    """

    if not _staff_only(request):
        messages.error(
            request,
            "Kitchen access is restricted to staff members.",
        )
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen:dashboard")

    order = get_object_or_404(
        Order.objects.select_related(
            "session",
            "session__table",
        ),
        id=order_id,
    )

    if order.status != "accepted":
        messages.warning(
            request,
            "Only accepted orders can be moved to preparation.",
        )
        return redirect("kitchen:dashboard")

    order.status = "preparing"
    order.preparing_at = timezone.now()

    order.save(
        update_fields=[
            "status",
            "preparing_at",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Order #{order.id} is now being prepared.",
    )

    return redirect("kitchen:dashboard")


# ============================================================
# MARK ORDER READY
# ============================================================

@login_required
def mark_ready(request, order_id):
    """
    Chef marks an order as ready for service.
    """

    if not _staff_only(request):
        messages.error(
            request,
            "Kitchen access is restricted to staff members.",
        )
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen:dashboard")

    order = get_object_or_404(
        Order.objects.select_related(
            "session",
            "session__table",
        ),
        id=order_id,
    )

    if order.status != "preparing":
        messages.warning(
            request,
            "Only orders currently being prepared can be marked ready.",
        )
        return redirect("kitchen:dashboard")

    order.status = "ready"
    order.ready_at = timezone.now()

    order.save(
        update_fields=[
            "status",
            "ready_at",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Order #{order.id} is ready for service.",
    )

    return redirect("kitchen:dashboard")