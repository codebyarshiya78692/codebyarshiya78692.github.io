from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render

from orders.models import DiningSession, Order, OrderItem
from restaurant.models import DiningTable, MenuItem


@login_required
def dashboard(request):
    """
    Main ERP reporting dashboard.

    Reports are calculated directly from the operational database:
    DiningSession -> Order -> OrderItem.

    No duplicate reporting data is stored, which keeps the reporting
    module scalable as the restaurant grows.
    """

    if not request.user.is_staff:
        return render(
            request,
            "reports/dashboard.html",
            {
                "access_denied": True,
            },
        )

    today = datetime.now().date()

    period = request.GET.get("period", "today")

    if period == "7days":
        start_date = today - timedelta(days=6)
        period_label = "Last 7 Days"

    elif period == "30days":
        start_date = today - timedelta(days=29)
        period_label = "Last 30 Days"

    elif period == "all":
        start_date = None
        period_label = "All Time"

    else:
        start_date = today
        period_label = "Today"

    orders = Order.objects.exclude(
        status="cancelled"
    ).select_related(
        "session",
        "session__table",
    )

    if start_date:
        orders = orders.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=today,
        )

    order_items = OrderItem.objects.filter(
        order__in=orders
    )

    # ---------------------------------------------------------
    # SALES
    # ---------------------------------------------------------

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

    cancelled_orders = Order.objects.filter(
        status="cancelled"
    )

    if start_date:
        cancelled_orders = cancelled_orders.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=today,
        )

    cancelled_count = cancelled_orders.count()

    # ---------------------------------------------------------
    # AVERAGE ORDER VALUE
    # ---------------------------------------------------------

    if total_orders:
        average_order_value = (
            total_revenue / total_orders
        )
    else:
        average_order_value = Decimal("0.00")

    # ---------------------------------------------------------
    # TOP SELLING MENU ITEMS
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # ORDER STATUS BREAKDOWN
    # ---------------------------------------------------------

    status_breakdown = (
        orders
        .values("status")
        .annotate(
            count=Count("id")
        )
        .order_by("-count")
    )

    # ---------------------------------------------------------
    # TABLE USAGE
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # CUSTOMER SESSIONS
    # ---------------------------------------------------------

    total_sessions = (
        DiningSession.objects
        .filter(
            orders__in=orders
        )
        .distinct()
        .count()
    )

    # ---------------------------------------------------------
    # MENU STATISTICS
    # ---------------------------------------------------------

    total_menu_items = MenuItem.objects.count()

    available_menu_items = MenuItem.objects.filter(
        is_available=True
    ).count()

    unavailable_menu_items = MenuItem.objects.filter(
        is_available=False
    ).count()

    total_tables = DiningTable.objects.count()

    available_tables = DiningTable.objects.filter(
        status="available"
    ).count()

    occupied_tables = DiningTable.objects.exclude(
        status="available"
    ).count()

    context = {
        "period": period,
        "period_label": period_label,
        "start_date": start_date,
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