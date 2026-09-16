from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import DiningTable, MenuCategory, MenuItem
from orders.models import DiningSession, Order, OrderItem


# ============================================================
# HOME
# ============================================================

def home(request):
    return render(
        request,
        "restaurant/home.html"
    )


# ============================================================
# TABLE SELECTION
# ============================================================

def table_selection(request):
    tables = (
        DiningTable.objects
        .all()
        .order_by("table_number")
    )

    return render(
        request,
        "restaurant/table_selection.html",
        {
            "tables": tables,
        }
    )


# ============================================================
# START DINING SESSION
# ============================================================

def start_dining(request, table_id):

    table = get_object_or_404(
        DiningTable,
        id=table_id
    )

    # A customer can only start a new dining session
    # on an available or completed table.
    if table.status not in ["available", "completed"]:

        messages.error(
            request,
            f"Table {table.table_number} is currently unavailable."
        )

        return redirect("table_selection")

    # Check whether this table already has an active session.
    active_session = (
        DiningSession.objects
        .filter(
            table=table,
            status="active"
        )
        .order_by("-started_at")
        .first()
    )

    if active_session:

        session = active_session

    else:

        session = DiningSession.objects.create(
            table=table,
            status="active"
        )

    # Mark the table as occupied.
    table.status = "occupied"

    table.save(
        update_fields=["status"]
    )

    # Store the customer's dining session
    # in the browser session.
    request.session["dining_session_id"] = session.id
    request.session["table_id"] = table.id

    # Do not destroy an existing cart.
    if "cart" not in request.session:
        request.session["cart"] = {}

    request.session.modified = True

    return redirect(
        "menu",
        table_id=table.id
    )


# ============================================================
# DIGITAL MENU
# ============================================================

def menu(request, table_id):

    table = get_object_or_404(
        DiningTable,
        id=table_id
    )

    session_id = request.session.get(
        "dining_session_id"
    )

    session = None

    if session_id:

        session = (
            DiningSession.objects
            .filter(
                id=session_id,
                table=table,
                status="active"
            )
            .first()
        )

    # A customer must have an active dining session
    # before accessing the menu.
    if session is None:

        return redirect(
            "table_selection"
        )

    categories = (
        MenuCategory.objects
        .prefetch_related("items")
        .all()
    )

    cart = request.session.get(
        "cart",
        {}
    )

    cart_count = sum(
        int(quantity)
        for quantity in cart.values()
    )

    return render(
        request,
        "restaurant/menu.html",
        {
            "table": table,
            "session": session,
            "categories": categories,
            "cart_count": cart_count,
        }
    )


# ============================================================
# ADD ITEM TO CART
# ============================================================

def add_to_cart(request, item_id):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method.",
            },
            status=405
        )

    item = get_object_or_404(
        MenuItem,
        id=item_id,
        is_available=True
    )

    if not request.session.get(
        "dining_session_id"
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "Please select a table first.",
            },
            status=400
        )

    try:

        quantity = int(
            request.POST.get(
                "quantity",
                1
            )
        )

    except (
        TypeError,
        ValueError
    ):

        quantity = 1

    quantity = max(
        1,
        min(quantity, 20)
    )

    cart = request.session.get(
        "cart",
        {}
    )

    item_key = str(
        item.id
    )

    current_quantity = int(
        cart.get(
            item_key,
            0
        )
    )

    new_quantity = min(
        current_quantity + quantity,
        20
    )

    cart[item_key] = new_quantity

    request.session["cart"] = cart
    request.session.modified = True

    cart_count = sum(
        int(value)
        for value in cart.values()
    )

    return JsonResponse(
        {
            "success": True,
            "message": f"{item.name} added to cart.",
            "cart_count": cart_count,
        }
    )


# ============================================================
# CART
# ============================================================

def cart(request):

    session_id = request.session.get(
        "dining_session_id"
    )

    table_id = request.session.get(
        "table_id"
    )

    # No active table/session means the customer
    # must select a table first.
    if not session_id or not table_id:

        return redirect(
            "table_selection"
        )

    session = get_object_or_404(
        DiningSession.objects.select_related("table"),
        id=session_id,
        table_id=table_id,
        status="active"
    )

    cart_data = request.session.get(
        "cart",
        {}
    )

    item_ids = []

    for item_id in cart_data.keys():

        try:

            item_ids.append(
                int(item_id)
            )

        except (
            TypeError,
            ValueError
        ):

            continue

    menu_items = (
        MenuItem.objects
        .filter(
            id__in=item_ids,
            is_available=True
        )
    )

    item_map = {
        str(item.id): item
        for item in menu_items
    }

    cart_items = []

    subtotal = Decimal(
        "0.00"
    )

    for item_id, quantity in cart_data.items():

        item = item_map.get(
            str(item_id)
        )

        if not item:
            continue

        quantity = max(
            1,
            int(quantity)
        )

        item_total = (
            item.price * quantity
        )

        subtotal += item_total

        cart_items.append(
            {
                "item": item,
                "quantity": quantity,
                "total": item_total,
            }
        )

    return render(
        request,
        "restaurant/cart.html",
        {
            "session": session,
            "table": session.table,
            "cart_items": cart_items,
            "subtotal": subtotal,
        }
    )


# ============================================================
# UPDATE CART
# ============================================================

def update_cart(request, item_id):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method.",
            },
            status=405
        )

    cart = request.session.get(
        "cart",
        {}
    )

    item_key = str(
        item_id
    )

    if item_key not in cart:

        return JsonResponse(
            {
                "success": False,
                "message": "Item is not in your cart.",
            },
            status=404
        )

    try:

        quantity = int(
            request.POST.get(
                "quantity",
                1
            )
        )

    except (
        TypeError,
        ValueError
    ):

        quantity = 1

    if quantity <= 0:

        cart.pop(
            item_key,
            None
        )

    else:

        cart[item_key] = min(
            quantity,
            20
        )

    request.session["cart"] = cart
    request.session.modified = True

    return redirect(
        "cart"
    )


# ============================================================
# PLACE ORDER
# ============================================================

@transaction.atomic
def place_order(request):

    if request.method != "POST":

        return redirect(
            "cart"
        )

    session_id = request.session.get(
        "dining_session_id"
    )

    if not session_id:

        return redirect(
            "table_selection"
        )

    session = get_object_or_404(
        DiningSession.objects.select_related("table"),
        id=session_id,
        status="active"
    )

    cart_data = request.session.get(
        "cart",
        {}
    )

    if not cart_data:

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect(
            "cart"
        )

    special_instructions = (
        request.POST
        .get(
            "special_instructions",
            ""
        )
        .strip()
    )

    order = Order.objects.create(
        session=session,
        status="new",
        special_instructions=special_instructions
    )

    item_ids = []

    for item_id in cart_data.keys():

        try:

            item_ids.append(
                int(item_id)
            )

        except (
            TypeError,
            ValueError
        ):

            continue

    menu_items = (
        MenuItem.objects
        .filter(
            id__in=item_ids,
            is_available=True
        )
    )

    item_map = {
        item.id: item
        for item in menu_items
    }

    valid_item_count = 0

    for item_id, quantity in cart_data.items():

        try:

            numeric_item_id = int(
                item_id
            )

        except (
            TypeError,
            ValueError
        ):

            continue

        menu_item = item_map.get(
            numeric_item_id
        )

        if not menu_item:
            continue

        quantity = max(
            1,
            int(quantity)
        )

        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            item_name=menu_item.name,
            unit_price=menu_item.price,
            quantity=quantity
        )

        valid_item_count += 1

    if valid_item_count == 0:

        order.delete()

        messages.error(
            request,
            "None of the selected menu items are currently available."
        )

        return redirect(
            "cart"
        )

    # The table now has an active order.
    table = session.table

    table.status = "order_in_progress"

    table.save(
        update_fields=["status"]
    )

    # Clear cart after successful order.
    request.session["cart"] = {}

    request.session["last_order_id"] = order.id

    request.session.modified = True

    return redirect(
        "order_confirmation",
        order_id=order.id
    )


# ============================================================
# ORDER CONFIRMATION
# ============================================================

def order_confirmation(request, order_id):

    session_id = request.session.get(
        "dining_session_id"
    )

    order = get_object_or_404(
        Order.objects
        .select_related(
            "session__table"
        )
        .prefetch_related(
            "items"
        ),
        id=order_id,
        session_id=session_id
    )

    return render(
        request,
        "restaurant/order_confirmation.html",
        {
            "order": order,
            "session": order.session,
        }
    )


# ============================================================
# ORDER TRACKING
# ============================================================

def order_tracking(request, order_id):

    session_id = request.session.get(
        "dining_session_id"
    )

    order = get_object_or_404(
        Order.objects
        .select_related(
            "session__table"
        )
        .prefetch_related(
            "items"
        ),
        id=order_id,
        session_id=session_id
    )

    status_steps = [
        (
            "new",
            "Order Received"
        ),
        (
            "accepted",
            "Accepted by Kitchen"
        ),
        (
            "preparing",
            "Preparing"
        ),
        (
            "ready",
            "Ready"
        ),
        (
            "served",
            "Served"
        ),
        (
            "completed",
            "Completed"
        ),
    ]

    status_order = [
        "new",
        "accepted",
        "preparing",
        "ready",
        "served",
        "completed",
    ]

    if order.status in status_order:

        current_index = status_order.index(
            order.status
        )

    else:

        current_index = 0

    return render(
        request,
        "restaurant/order_tracking.html",
        {
            "order": order,
            "status_steps": status_steps,
            "current_index": current_index,
        }
    )