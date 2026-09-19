from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from orders.models import DiningSession, Order, OrderItem
from restaurant.models import DiningTable, MenuItem


@login_required
def dashboard(request):
    """
    Main IDDS reporting dashboard.

    Reports are calculated directly from operational data:
    DiningSession -> Order -> OrderItem.
    """

    if not request.user.is_authenticated or not request.user.is_superuser:
        return render(
            request,
            "reports/dashboard.html",
            {
                "access_denied": True,
            },
        )

    today = timezone.localdate()

    # =========================================================
    # REPORT PERIOD
    # =========================================================

    period = request.GET.get("period", "today")

    start_date = today
    end_date = today
    period_label = "Today"

    if period == "week":
        # Monday through today
        start_date = today - timedelta(days=today.weekday())
        period_label = "This Week"

    elif period == "month":
        start_date = today.replace(day=1)
        period_label = "This Month"

    elif period == "custom":
        custom_start = request.GET.get("start_date")
        custom_end = request.GET.get("end_date")

        if custom_start and custom_end:
            try:
                from datetime import date

                parsed_start = date.fromisoformat(custom_start)
                parsed_end = date.fromisoformat(custom_end)

                if parsed_start <= parsed_end:
                    start_date = parsed_start
                    end_date = parsed_end
                    period_label = (
                        f"{start_date.strftime('%d %b %Y')} "
                        f"— {end_date.strftime('%d %b %Y')}"
                    )
                else:
                    period = "today"
                    period_label = "Today"

            except ValueError:
                period = "today"
                period_label = "Today"

    # =========================================================
    # ORDERS
    # =========================================================

    orders = (
        Order.objects
        .exclude(status="cancelled")
        .select_related(
            "session",
            "session__table",
        )
    )

    orders = orders.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    )

    # =========================================================
    # ORDER ITEMS / REVENUE
    # =========================================================

    order_items = OrderItem.objects.filter(
        order__in=orders
    )

    item_revenue_expression = ExpressionWrapper(
        F("unit_price") * F("quantity"),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2,
        ),
    )

    total_revenue = order_items.aggregate(
        total=Coalesce(
            Sum(item_revenue_expression),
            Decimal("0.00"),
        )
    )["total"]

    total_orders = orders.count()

    completed_orders = orders.filter(
        status="completed"
    ).count()

    active_orders = orders.filter(
        status__in=[
            "new",
            "accepted",
            "preparing",
            "ready",
            "served",
        ]
    ).count()

    # =========================================================
    # CANCELLED ORDERS
    # =========================================================

    cancelled_count = (
        Order.objects
        .filter(status="cancelled")
        .filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        )
        .count()
    )

    # =========================================================
    # AVERAGE ORDER VALUE
    # =========================================================

    if total_orders:
        average_order_value = (
            total_revenue / total_orders
        )
    else:
        average_order_value = Decimal("0.00")

    # =========================================================
    # TOP SELLING MENU ITEMS
    # =========================================================

    top_items = (
        order_items
        .values(
            "menu_item_id",
            "item_name",
        )
        .annotate(
            quantity_sold=Coalesce(
                Sum("quantity"),
                0,
            ),
            revenue=Coalesce(
                Sum(item_revenue_expression),
                Decimal("0.00"),
            ),
        )
        .order_by(
            "-quantity_sold",
            "-revenue",
        )[:10]
    )

    # =========================================================
    # ORDER STATUS
    # =========================================================

    status_breakdown = (
        orders
        .values("status")
        .annotate(
            count=Count("id")
        )
        .order_by("-count")
    )

    # =========================================================
    # TABLE USAGE
    # =========================================================

    table_usage = (
        DiningSession.objects
        .filter(
            orders__in=orders
        )
        .values(
            "table__table_number"
        )
        .annotate(
            session_count=Count(
                "id",
                distinct=True,
            ),
            order_count=Count(
                "orders",
                distinct=True,
            ),
        )
        .order_by(
            "-order_count",
            "table__table_number",
        )[:10]
    )

    # =========================================================
    # DINING SESSIONS FOR SELECTED PERIOD
    # =========================================================

    period_sessions = DiningSession.objects.filter(
        started_at__date__gte=start_date,
        started_at__date__lte=end_date,
    )

    total_sessions = period_sessions.count()

    completed_sessions = period_sessions.filter(
        status="completed"
    ).count()

    # =========================================================
    # CURRENT ACTIVE SESSIONS
    # =========================================================

    active_sessions = DiningSession.objects.filter(
        status="active"
    ).count()

    # =========================================================
    # MENU STATISTICS
    # =========================================================

    total_menu_items = MenuItem.objects.count()

    available_menu_items = MenuItem.objects.filter(
        is_available=True
    ).count()

    unavailable_menu_items = MenuItem.objects.filter(
        is_available=False
    ).count()

    # =========================================================
    # TABLE STATISTICS
    # =========================================================

    total_tables = DiningTable.objects.count()

    available_tables = DiningTable.objects.filter(
        status="available"
    ).count()

    occupied_tables = DiningTable.objects.exclude(
        status="available"
    ).count()

    # =========================================================
    # CONTEXT
    # =========================================================

    context = {
        "period": period,
        "period_label": period_label,

        "start_date": start_date,
        "end_date": end_date,
        "today": today,

        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "active_orders": active_orders,
        "cancelled_count": cancelled_count,
        "average_order_value": average_order_value,

        "top_items": top_items,
        "status_breakdown": status_breakdown,
        "table_usage": table_usage,

        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "active_sessions": active_sessions,

        "total_menu_items": total_menu_items,
        "available_menu_items": available_menu_items,
        "unavailable_menu_items": unavailable_menu_items,

        "total_tables": total_tables,
        "available_tables": available_tables,
        "occupied_tables": occupied_tables,

        "access_denied": False,
    }

    return render(
        request,
        "reports/dashboard.html",
        context,
    )