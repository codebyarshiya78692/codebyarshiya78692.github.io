from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from orders.models import Order, ServiceRequest


# ============================================================
# STAFF ACCESS
# ============================================================

def _staff_only(request):
    """
    Kitchen is an internal staff area.
    """

    if not request.user.is_authenticated:
        return False

    return request.user.is_staff


def _check_staff(request):
    """
    Shared staff-access helper.

    Returns True when the current user is staff.
    Otherwise sends them back to the home page.
    """

    if not _staff_only(request):
        messages.error(
            request,
            "Kitchen access is restricted to staff members.",
        )
        return False

    return True


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
    """

    if not _check_staff(request):
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

    if not _check_staff(request):
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
            f"Order #{order.id} is already "
            f"{order.get_status_display().lower()}.",
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

    if not _check_staff(request):
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

    if not _check_staff(request):
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
            "Only orders currently being prepared "
            "can be marked ready.",
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


# ============================================================
# SERVICE REQUESTS DASHBOARD
# ============================================================

@login_required
def service_requests_dashboard(request):
    """
    Staff dashboard for customer service requests.
    """

    if not _check_staff(request):
        return redirect("home")

    service_requests = (
        ServiceRequest.objects
        .select_related(
            "session",
            "session__table",
        )
        .order_by(
            "status",
            "requested_at",
        )
    )

    active_requests = service_requests.filter(
        status__in=[
            "requested",
            "accepted",
        ]
    )

    completed_requests = service_requests.filter(
        status="completed",
    )[:50]

    requested_count = service_requests.filter(
        status="requested",
    ).count()

    accepted_count = service_requests.filter(
        status="accepted",
    ).count()

    completed_count = service_requests.filter(
        status="completed",
    ).count()

    return render(
        request,
        "kitchen/service_requests.html",
        {
            "service_requests": service_requests,
            "active_requests": active_requests,
            "completed_requests": completed_requests,
            "requested_count": requested_count,
            "accepted_count": accepted_count,
            "completed_count": completed_count,
        },
    )


# ============================================================
# ACCEPT SERVICE REQUEST
# ============================================================

@login_required
def accept_service_request(request, request_id):
    """
    Staff accepts a customer service request.
    """

    if not _check_staff(request):
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen:service_requests")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
    )

    if service_request.status != "requested":
        messages.warning(
            request,
            "This service request is no longer waiting.",
        )
        return redirect("kitchen:service_requests")

    service_request.status = "accepted"

    service_request.save(
        update_fields=[
            "status",
        ]
    )

    messages.success(
        request,
        "Service request accepted.",
    )

    return redirect("kitchen:service_requests")


# ============================================================
# COMPLETE SERVICE REQUEST
# ============================================================

@login_required
def complete_service_request(request, request_id):
    """
    Staff marks a service request as completed.
    """

    if not _check_staff(request):
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen:service_requests")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
    )

    if service_request.status == "completed":
        messages.info(
            request,
            "This service request is already completed.",
        )
        return redirect("kitchen:service_requests")

    service_request.status = "completed"
    service_request.completed_at = timezone.now()

    service_request.save(
        update_fields=[
            "status",
            "completed_at",
        ]
    )

    messages.success(
        request,
        "Service request marked as completed.",
    )

    return redirect("kitchen:service_requests") 