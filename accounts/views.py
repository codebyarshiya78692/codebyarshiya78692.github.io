from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from orders.models import DiningSession, Order, ServiceRequest


# ============================================================
# ROLE HELPERS
# ============================================================

def _is_chef(user):
    """
    Return True when the authenticated user belongs
    to the Chef group.
    """

    if not user.is_authenticated:
        return False

    return (
        user.groups
        .filter(name__iexact="chef")
        .exists()
    )


def _is_waiter(user):
    """
    Return True when the authenticated user belongs
    to the Waiter group.
    """

    if not user.is_authenticated:
        return False

    return (
        user.groups
        .filter(name__iexact="waiter")
        .exists()
    )


def _staff_role(user):
    """
    Determine the staff role for the authenticated user.

    Priority:
        1. Superuser -> admin
        2. Chef group -> chef
        3. Waiter group -> waiter
        4. Username fallback for demo accounts
        5. Other staff -> staff
        6. Normal user -> customer
    """

    if not user.is_authenticated:
        return "anonymous"

    if user.is_superuser:
        return "admin"

    if _is_chef(user):
        return "chef"

    if _is_waiter(user):
        return "waiter"

    username = user.username.lower()

    if "chef" in username:
        return "chef"

    if "waiter" in username:
        return "waiter"

    if user.is_staff:
        return "staff"

    return "customer"


# ============================================================
# LOGIN
# ============================================================

def customer_login(request):
    """
    Unified IDDS login.

    Customers are sent into the digital dining flow.

    Staff are automatically sent to their role-specific
    dashboard:

        Admin  -> Django Admin
        Chef   -> Kitchen Dashboard
        Waiter -> Waiter Dashboard
    """

    if request.user.is_authenticated:

        return _redirect_after_login(
            request.user
        )

    if request.method == "POST":

        username = (
            request.POST
            .get("username", "")
            .strip()
        )

        password = request.POST.get(
            "password",
            "",
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            if not user.is_active:

                messages.error(
                    request,
                    "This account is inactive.",
                )

                return render(
                    request,
                    "accounts/login.html",
                )

            login(
                request,
                user,
            )

            return _redirect_after_login(
                user
            )

        messages.error(
            request,
            "Invalid username or password. Please try again.",
        )

    return render(
        request,
        "accounts/login.html",
    )


def _redirect_after_login(user):
    """
    Central login-routing function.
    """

    role = _staff_role(user)

    if role == "admin":
        return redirect("/admin/")

    if role == "chef":
        return redirect("kitchen:dashboard")

    if role == "waiter":
        return redirect("accounts:waiter_dashboard")

    if role == "staff":
        return redirect("accounts:staff_dashboard")

    return redirect("table_selection")


# ============================================================
# CHEF LOGIN
# ============================================================

def chef_login(request):
    """
    Dedicated Chef login.

    Only users belonging to the Chef group, or the existing
    Chef demo-account fallback, can enter the kitchen dashboard.
    """

    if request.user.is_authenticated:

        role = _staff_role(request.user)

        if role == "chef":
            return redirect(
                "kitchen:dashboard"
            )

        logout(request)

    if request.method == "POST":

        username = (
            request.POST
            .get("username", "")
            .strip()
        )

        password = request.POST.get(
            "password",
            "",
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            if not user.is_active:

                messages.error(
                    request,
                    "This account is inactive.",
                )

                return render(
                    request,
                    "accounts/login.html",
                    {
                        "login_role": "chef",
                    },
                )

            if _staff_role(user) == "chef":

                login(
                    request,
                    user,
                )

                messages.success(
                    request,
                    "Welcome to the IDDS Kitchen Dashboard.",
                )

                return redirect(
                    "kitchen:dashboard"
                )

        messages.error(
            request,
            "This account is not registered as a Chef.",
        )

    return render(
        request,
        "accounts/login.html",
        {
            "login_role": "chef",
        },
    )


# ============================================================
# WAITER LOGIN
# ============================================================

def waiter_login(request):
    """
    Dedicated Waiter login.

    Only users belonging to the Waiter group, or the existing
    Waiter demo-account fallback, can enter the waiter dashboard.
    """

    if request.user.is_authenticated:

        role = _staff_role(request.user)

        if role == "waiter":
            return redirect(
                "accounts:waiter_dashboard"
            )

        logout(request)

    if request.method == "POST":

        username = (
            request.POST
            .get("username", "")
            .strip()
        )

        password = request.POST.get(
            "password",
            "",
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            if not user.is_active:

                messages.error(
                    request,
                    "This account is inactive.",
                )

                return render(
                    request,
                    "accounts/login.html",
                    {
                        "login_role": "waiter",
                    },
                )

            if _staff_role(user) == "waiter":

                login(
                    request,
                    user,
                )

                messages.success(
                    request,
                    "Welcome to the IDDS Service Dashboard.",
                )

                return redirect(
                    "accounts:waiter_dashboard"
                )

        messages.error(
            request,
            "This account is not registered as a Waiter.",
        )

    return render(
        request,
        "accounts/login.html",
        {
            "login_role": "waiter",
        },
    )


# ============================================================
# CUSTOMER DASHBOARD
# ============================================================

@login_required
def dashboard(request):
    """
    Customer account dashboard.

    The main customer experience remains table-based,
    but authenticated customers can still see their
    recent activity here.
    """

    role = _staff_role(request.user)

    if role == "admin":
        return redirect("/admin/")

    if role == "chef":
        return redirect("kitchen:dashboard")

    if role == "waiter":
        return redirect("accounts:waiter_dashboard")

    if role == "staff":
        return redirect("accounts:staff_dashboard")

    recent_orders = (
        Order.objects
        .filter(
            session__customer_name=request.user.username,
        )
        .select_related(
            "session",
            "session__table",
        )
        .prefetch_related(
            "items",
        )
        .order_by(
            "-created_at"
        )[:5]
    )

    active_order = (
        Order.objects
        .filter(
            session__customer_name=request.user.username,
            status__in=[
                "new",
                "accepted",
                "preparing",
                "ready",
                "served",
            ],
        )
        .select_related(
            "session",
            "session__table",
        )
        .order_by(
            "-created_at"
        )
        .first()
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "recent_orders": recent_orders,
            "active_order": active_order,
        },
    )


# ============================================================
# WAITER DASHBOARD
# ============================================================

@login_required
def waiter_dashboard(request):
    """
    Waiter operational dashboard.

    Waiters can see:

        - Active dining tables
        - Pending service requests
        - Accepted service requests
        - Orders ready to be served
        - Recently completed service requests
    """

    if _staff_role(request.user) != "waiter":

        messages.error(
            request,
            "Waiter access is restricted to waiter accounts.",
        )

        return redirect("home")

    active_sessions = (
        DiningSession.objects
        .filter(
            status="active",
        )
        .select_related(
            "table",
        )
        .prefetch_related(
            "orders",
        )
        .order_by(
            "table__table_number",
        )
    )

    pending_requests = (
        ServiceRequest.objects
        .filter(
            status="requested",
        )
        .select_related(
            "session",
            "session__table",
        )
        .order_by(
            "requested_at",
        )
    )

    accepted_requests = (
        ServiceRequest.objects
        .filter(
            status="accepted",
        )
        .select_related(
            "session",
            "session__table",
        )
        .order_by(
            "requested_at",
        )
    )

    ready_orders = (
        Order.objects
        .filter(
            status="ready",
        )
        .select_related(
            "session",
            "session__table",
        )
        .prefetch_related(
            "items",
        )
        .order_by(
            "ready_at",
        )
    )

    completed_requests = (
        ServiceRequest.objects
        .filter(
            status="completed",
        )
        .select_related(
            "session",
            "session__table",
        )
        .order_by(
            "-completed_at",
        )[:20]
    )

    return render(
        request,
        "accounts/waiter_dashboard.html",
        {
            "active_sessions": active_sessions,
            "pending_requests": pending_requests,
            "accepted_requests": accepted_requests,
            "ready_orders": ready_orders,
            "completed_requests": completed_requests,
        },
    )


# ============================================================
# WAITER - ACCEPT SERVICE REQUEST
# ============================================================

@login_required
def waiter_accept_request(request, request_id):

    if _staff_role(request.user) != "waiter":

        messages.error(
            request,
            "Only waiters can manage service requests.",
        )

        return redirect("home")

    if request.method != "POST":

        return redirect(
            "accounts:waiter_dashboard"
        )

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
    )

    if service_request.status != "requested":

        messages.warning(
            request,
            "This service request is no longer waiting.",
        )

        return redirect(
            "accounts:waiter_dashboard"
        )

    service_request.status = "accepted"

    service_request.save(
        update_fields=[
            "status",
        ]
    )

    messages.success(
        request,
        (
            f"Service request for Table "
            f"{service_request.session.table.table_number} "
            f"has been accepted."
        ),
    )

    return redirect(
        "accounts:waiter_dashboard"
    )


# ============================================================
# WAITER - COMPLETE SERVICE REQUEST
# ============================================================

@login_required
def waiter_complete_request(request, request_id):

    if _staff_role(request.user) != "waiter":

        messages.error(
            request,
            "Only waiters can manage service requests.",
        )

        return redirect("home")

    if request.method != "POST":

        return redirect(
            "accounts:waiter_dashboard"
        )

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
    )

    if service_request.status != "accepted":

        messages.warning(
            request,
            "Only accepted requests can be completed.",
        )

        return redirect(
            "accounts:waiter_dashboard"
        )

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
        (
            f"Service request for Table "
            f"{service_request.session.table.table_number} "
            f"has been completed."
        ),
    )

    return redirect(
        "accounts:waiter_dashboard"
    )


# ============================================================
# WAITER - SERVE READY ORDER
# ============================================================

@login_required
def waiter_serve_order(request, order_id):

    if _staff_role(request.user) != "waiter":

        messages.error(
            request,
            "Only waiters can serve customer orders.",
        )

        return redirect("home")

    if request.method != "POST":

        return redirect(
            "accounts:waiter_dashboard"
        )

    order = get_object_or_404(
        Order.objects.select_related(
            "session",
            "session__table",
        ),
        id=order_id,
    )

    if order.status != "ready":

        messages.warning(
            request,
            "Only ready orders can be served.",
        )

        return redirect(
            "accounts:waiter_dashboard"
        )

    order.status = "served"
    order.served_at = timezone.now()

    order.save(
        update_fields=[
            "status",
            "served_at",
            "updated_at",
        ]
    )

    messages.success(
        request,
        (
            f"Order #{order.id} has been marked "
            f"as served to Table "
            f"{order.session.table.table_number}."
        ),
    )

    return redirect(
        "accounts:waiter_dashboard"
    )


# ============================================================
# GENERIC STAFF LANDING PAGE
# ============================================================

@login_required
def staff_dashboard(request):

    if not request.user.is_staff:

        return redirect("home")

    role = _staff_role(
        request.user
    )

    if role == "admin":
        return redirect("/admin/")

    if role == "chef":
        return redirect("kitchen:dashboard")

    if role == "waiter":
        return redirect("accounts:waiter_dashboard")

    return render(
        request,
        "accounts/staff_dashboard.html",
        {
            "role": role,
        },
    )


# ============================================================
# LOGOUT
# ============================================================

def customer_logout(request):

    logout(request)

    return redirect("home")