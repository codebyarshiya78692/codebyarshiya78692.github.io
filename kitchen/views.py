from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from inventory.services import deduct_inventory_for_order
from orders.models import Order, ServiceRequest


# ============================================================
# STAFF ACCESS
# ============================================================

def _staff_only(request):
    """
    Kitchen is an internal Chef-only area.
    """

    if not request.user.is_authenticated:
        return False

    return request.user.groups.filter(
        name="Chef"
    ).exists()


def _check_staff(request):
    """
    Shared Chef-access helper.

    Returns True when the current user is a Chef.
    Otherwise sends them back to the home page.
    """

    if not _staff_only(request):
        messages.error(
            request,
            "Kitchen access is restricted to Chef staff.",
        )

        return False

    return True


# ============================================================
# KITCHEN DASHBOARD
# ============================================================

@login_required
def kitchen_dashboard(request):
    """
    Main Chef dashboard.

    Shows active kitchen orders:

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
            "created_at",
        )
    )

    new_orders = orders.filter(
        status="new",
    )

    accepted_orders = orders.filter(
        status="accepted",
    )

    preparing_orders = orders.filter(
        status="preparing",
    )

    ready_orders = orders.filter(
        status="ready",
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
    Chef accepts a newly received food order.
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
            (
                f"Order #{order.id} is already "
                f"{order.get_status_display().lower()}."
            ),
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
        (
            f"Order #{order.id} has been accepted "
            "by the kitchen."
        ),
    )

    return redirect("kitchen:dashboard")


# ============================================================
# START PREPARING
# ============================================================

@login_required
def start_preparing(request, order_id):
    """
    Move an accepted order into preparation.

    Inventory is deducted at this point because the kitchen
    has actually started preparing the food.
    """

    if not _check_staff(request):
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen:dashboard")

    order = get_object_or_404(
        Order.objects
        .select_related(
            "session",
            "session__table",
        )
        .prefetch_related(
            "items",
        ),
        id=order_id,
    )

    if order.status != "accepted":

        messages.warning(
            request,
            (
                "Only accepted orders can be moved "
                "to preparation."
            ),
        )

        return redirect("kitchen:dashboard")

    # --------------------------------------------------------
    # INVENTORY DEDUCTION
    # --------------------------------------------------------

    inventory_result = deduct_inventory_for_order(
        order
    )

    if not inventory_result["success"]:

        messages.error(
            request,
            (
                f"Order #{order.id} cannot start preparation: "
                f"{inventory_result['message']}"
            ),
        )

        return redirect("kitchen:dashboard")

    # --------------------------------------------------------
    # START PREPARATION
    # --------------------------------------------------------

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
        (
            f"Order #{order.id} is now being prepared. "
            "Inventory has been updated."
        ),
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
            (
                "Only orders currently being prepared "
                "can be marked ready."
            ),
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
# CHEF SERVICE REQUESTS
# ============================================================

@login_required
def service_requests_dashboard(request):
    """
    Chef dashboard for customer food-related requests.

    Chef handles ONLY:

        assistance
        other

    Water, cutlery and bill requests belong to the Waiter.
    """

    if not _check_staff(request):
        return redirect("home")

    service_requests = (
        ServiceRequest.objects
        .filter(
            request_type__in=[
                "assistance",
                "other",
            ],
        )
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
# ACCEPT CHEF SERVICE REQUEST
# ============================================================

@login_required
def accept_service_request(request, request_id):
    """
    Chef accepts a food-related customer service request.

    Only:
        assistance
        other

    are allowed here.
    """

    if not _check_staff(request):
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen:service_requests")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        request_type__in=[
            "assistance",
            "other",
        ],
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
# COMPLETE CHEF SERVICE REQUEST
# ============================================================

@login_required
def complete_service_request(request, request_id):
    """
    Chef marks a food-related customer service request
    as completed.
    """

    if not _check_staff(request):
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen:service_requests")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        request_type__in=[
            "assistance",
            "other",
        ],
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