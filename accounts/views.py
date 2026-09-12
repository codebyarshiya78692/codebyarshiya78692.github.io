from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def customer_login(request):
    """
    Customer login page.

    Staff/superuser accounts are sent to Django Admin.
    Normal users are sent to the customer dashboard.
    """

    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("/admin/")
        return redirect("accounts:dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)

            if user.is_staff:
                return redirect("/admin/")

            return redirect("accounts:dashboard")

        messages.error(
            request,
            "Invalid username or password. Please try again.",
        )

    return render(
        request,
        "accounts/login.html",
    )


@login_required
def dashboard(request):
    """
    Customer dashboard.
    """

    if request.user.is_staff:
        return redirect("/admin/")

    from orders.models import Order

    recent_orders = (
        Order.objects
        .filter(session__customer_name=request.user.username)
        .select_related("session", "session__table")
        .prefetch_related("items")
        .order_by("-created_at")[:5]
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
        .select_related("session", "session__table")
        .order_by("-created_at")
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


def customer_logout(request):
    """
    Logout customer and return to home page.
    """

    logout(request)
    return redirect("home")