from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from orders.models import Order


# ============================================================
# STAFF ACCESS
# ============================================================

def _is_chef(request):
    """
    Only users belonging to the Chef group may access
    the kitchen.
    """

    if not request.user.is_authenticated:
        return False

    return request.user.groups.filter(
        name="Chef"
    ).exists()


def _staff_only(request):
    """
    Compatibility wrapper used by the kitchen views.
    """

    return _is_chef(
        request
    )


def _deny_kitchen_access(request):
    """
    Display a clear message and return the user to the
    public site.
    """

    messages.error(
        request,
        "Kitchen access is restricted to Chef staff.",
    )

    return redirect(
        "home"
    )


# ============================================================
# INVENTORY HELPERS
# ============================================================

def _deduct_inventory_for_order(order):
    """
    Deduct ingredient stock when the Chef actually starts
    preparing an order.

    The function is deliberately defensive because the current
    project may contain menu/recipe inventory relations in
    different versions.

    Supported recipe patterns include:

        menu_item.ingredients
        menu_item.menu_ingredients
        menu_item.recipe_items

    A recipe quantity is multiplied by the ordered quantity.

    Example:

        Coffee recipe = 0.018 kg beans

        Order quantity = 5

        Deduction = 0.090 kg
    """

    try:
        from inventory.models import Ingredient, StockMovement
    except ImportError:
        return {
            "success": True,
            "message": "Inventory module is not available.",
        }

    total_requirements = {}

    # --------------------------------------------------------
    # COLLECT INGREDIENT REQUIREMENTS
    # --------------------------------------------------------

    for order_item in order.items.select_related(
        "menu_item"
    ).all():

        menu_item = order_item.menu_item
        order_quantity = Decimal(
            str(
                order_item.quantity
            )
        )

        possible_recipe_relations = [
            "menu_ingredients",
            "ingredients",
            "recipe_items",
        ]

        recipe_manager = None

        for relation_name in possible_recipe_relations:

            try:

                candidate = getattr(
                    menu_item,
                    relation_name,
                )

                if hasattr(
                    candidate,
                    "all",
                ):
                    recipe_manager = candidate
                    break

            except Exception:
                continue

        if recipe_manager is None:
            continue

        try:
            recipe_rows = recipe_manager.all()
        except Exception:
            continue

        for recipe_row in recipe_rows:

            ingredient = getattr(
                recipe_row,
                "ingredient",
                None,
            )

            if ingredient is None:

                if isinstance(
                    recipe_row,
                    Ingredient,
                ):
                    ingredient = recipe_row

            if ingredient is None:
                continue

            recipe_quantity = (
                getattr(
                    recipe_row,
                    "quantity",
                    None,
                )
                or getattr(
                    recipe_row,
                    "quantity_required",
                    None,
                )
                or getattr(
                    recipe_row,
                    "amount",
                    None,
                )
            )

            if recipe_quantity is None:
                continue

            required_quantity = (
                Decimal(
                    str(recipe_quantity)
                )
                * order_quantity
            )

            ingredient_id = ingredient.id

            if ingredient_id not in total_requirements:

                total_requirements[
                    ingredient_id
                ] = {
                    "ingredient": ingredient,
                    "quantity": Decimal("0.000"),
                }

            total_requirements[
                ingredient_id
            ]["quantity"] += required_quantity

    # --------------------------------------------------------
    # IF THIS ORDER HAS NO RECIPE DATA YET
    # --------------------------------------------------------

    if not total_requirements:

        return {
            "success": True,
            "message": (
                "No recipe-linked inventory items were "
                "configured for this order."
            ),
        }

    # --------------------------------------------------------
    # CHECK STOCK BEFORE DEDUCTING ANYTHING
    # --------------------------------------------------------

    for data in total_requirements.values():

        ingredient = data["ingredient"]
        required_quantity = data["quantity"]

        if ingredient.current_stock < required_quantity:

            return {
                "success": False,
                "message": (
                    f"Insufficient stock for "
                    f"{ingredient.name}. "
                    f"Available: "
                    f"{ingredient.current_stock} "
                    f"{ingredient.unit}; "
                    f"required: "
                    f"{required_quantity} "
                    f"{ingredient.unit}."
                ),
            }

    # --------------------------------------------------------
    # DEDUCT STOCK
    # --------------------------------------------------------

    for data in total_requirements.values():

        ingredient = data["ingredient"]
        required_quantity = data["quantity"]

        ingredient.current_stock = (
            ingredient.current_stock
            - required_quantity
        )

        ingredient.save(
            update_fields=[
                "current_stock",
                "updated_at",
            ],
        )

        StockMovement.objects.create(
            ingredient=ingredient,
            movement_type="usage",
            quantity=required_quantity,
            unit_cost=ingredient.cost_per_unit,
            reference=f"Order #{order.id}",
            notes=(
                "Inventory consumed when Chef "
                "started preparing the order."
            ),
        )

    return {
        "success": True,
        "message": "Inventory deducted successfully.",
    }


# ============================================================
# KITCHEN DASHBOARD
# ============================================================

@login_required
def kitchen_dashboard(request):
    """
    Chef dashboard.

    NEW orders:
        Visible to every Chef.

    ACCEPTED / PREPARING:
        Visible only to the Chef who accepted the order.

    READY:
        No longer part of the Chef's active work queue.
        It has moved to the waiter workflow.
    """

    if not _staff_only(request):

        return _deny_kitchen_access(
            request
        )

    chef = request.user

    # --------------------------------------------------------
    # NEW ORDERS
    #
    # Every Chef can see these.
    # --------------------------------------------------------

    new_orders = (
        Order.objects
        .filter(
            status="new",
            assigned_chef__isnull=True,
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

    # --------------------------------------------------------
    # THIS CHEF'S ASSIGNED ORDERS
    # --------------------------------------------------------

    my_orders = (
        Order.objects
        .filter(
            assigned_chef=chef,
            status__in=[
                "accepted",
                "preparing",
            ],
        )
        .select_related(
            "session",
            "session__table",
            "assigned_chef",
        )
        .prefetch_related(
            "items",
        )
        .order_by(
            "created_at",
        )
    )

    accepted_orders = my_orders.filter(
        status="accepted",
    )

    preparing_orders = my_orders.filter(
        status="preparing",
    )

    # --------------------------------------------------------
    # READY ORDERS
    #
    # They are included only for compatibility with the
    # existing template. They are no longer treated as the
    # Chef's active workload.
    # --------------------------------------------------------

    ready_orders = (
        Order.objects
        .filter(
            status="ready",
            assigned_chef=chef,
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

    # Existing template expects "orders".
    orders = list(new_orders) + list(my_orders)

    return render(
        request,
        "kitchen/dashboard.html",
        {
            "orders": orders,
            "new_orders": new_orders,
            "accepted_orders": accepted_orders,
            "preparing_orders": preparing_orders,
            "ready_orders": ready_orders,
            "chef": chef,
        },
    )


# ============================================================
# ACCEPT ORDER
# ============================================================

@login_required
@transaction.atomic
def accept_order(request, order_id):
    """
    Atomically claim a NEW order.

    This prevents two chefs from accepting the same order.
    """

    if not _staff_only(request):

        return _deny_kitchen_access(
            request
        )

    if request.method != "POST":

        return redirect(
            "kitchen:dashboard"
        )

    # select_for_update prevents two chefs from claiming
    # the same order at the same time.
    order = get_object_or_404(
        Order.objects
        .select_for_update()
        .select_related(
            "session",
            "session__table",
        ),
        id=order_id,
    )

    # --------------------------------------------------------
    # ONLY COMPLETELY UNASSIGNED NEW ORDERS CAN BE CLAIMED.
    # --------------------------------------------------------

    if (
        order.status != "new"
        or order.assigned_chef_id is not None
    ):

        messages.warning(
            request,
            (
                f"Order #{order.id} has already been "
                "accepted by another chef."
            ),
        )

        return redirect(
            "kitchen:dashboard"
        )

    order.status = "accepted"
    order.assigned_chef = request.user
    order.accepted_at = timezone.now()

    order.save(
        update_fields=[
            "status",
            "assigned_chef",
            "accepted_at",
            "updated_at",
        ],
    )

    messages.success(
        request,
        (
            f"Order #{order.id} is now assigned "
            f"to Chef {request.user.username}."
        ),
    )

    return redirect(
        "kitchen:dashboard"
    )


# ============================================================
# START PREPARING
# ============================================================

@login_required
@transaction.atomic
def start_preparing(request, order_id):
    """
    Start preparing an order owned by this Chef.

    Inventory is deducted here because this is the point at
    which the kitchen actually begins consuming ingredients.
    """

    if not _staff_only(request):

        return _deny_kitchen_access(
            request
        )

    if request.method != "POST":

        return redirect(
            "kitchen:dashboard"
        )

    order = get_object_or_404(
        Order.objects
        .select_for_update()
        .select_related(
            "session",
            "session__table",
        )
        .prefetch_related(
            "items",
        ),
        id=order_id,
        assigned_chef=request.user,
    )

    if order.status != "accepted":

        messages.warning(
            request,
            (
                "Only orders accepted by you can "
                "be started."
            ),
        )

        return redirect(
            "kitchen:dashboard"
        )

    # --------------------------------------------------------
    # INVENTORY
    # --------------------------------------------------------

    inventory_result = (
        _deduct_inventory_for_order(
            order
        )
    )

    if not inventory_result["success"]:

        messages.error(
            request,
            inventory_result["message"],
        )

        return redirect(
            "kitchen:dashboard"
        )

    order.status = "preparing"
    order.preparing_at = timezone.now()

    order.save(
        update_fields=[
            "status",
            "preparing_at",
            "updated_at",
        ],
    )

    messages.success(
        request,
        (
            f"Order #{order.id} is now being prepared. "
            "Required inventory has been deducted."
        ),
    )

    return redirect(
        "kitchen:dashboard"
    )


# ============================================================
# MARK ORDER READY
# ============================================================

@login_required
@transaction.atomic
def mark_ready(request, order_id):
    """
    Chef marks their own preparing order as ready.

    Once ready, the Chef's workflow is finished.
    The order is handed over to the Waiter.
    """

    if not _staff_only(request):

        return _deny_kitchen_access(
            request
        )

    if request.method != "POST":

        return redirect(
            "kitchen:dashboard"
        )

    order = get_object_or_404(
        Order.objects
        .select_for_update()
        .select_related(
            "session",
            "session__table",
            "assigned_chef",
        ),
        id=order_id,
        assigned_chef=request.user,
    )

    if order.status != "preparing":

        messages.warning(
            request,
            (
                "Only your orders currently being "
                "prepared can be marked ready."
            ),
        )

        return redirect(
            "kitchen:dashboard"
        )

    order.status = "ready"
    order.ready_at = timezone.now()

    order.save(
        update_fields=[
            "status",
            "ready_at",
            "updated_at",
        ],
    )

    messages.success(
        request,
        (
            f"Order #{order.id} is READY. "
            "It has moved to the waiter workflow."
        ),
    )

    return redirect(
        "kitchen:dashboard"
    )
# ============================================================
# CUSTOMER SERVICE REQUESTS
# ============================================================

@login_required
def service_requests_dashboard(request):
    """
    Compatibility service-request dashboard.

    Service requests are operationally handled by Waiters.
    This endpoint is retained because the existing kitchen
    URL configuration and service-request template reference
    these view names.

    Chef accounts are not allowed to manage service requests.
    Waiter accounts may access the dashboard.
    """

    if not request.user.is_authenticated:
        return redirect("accounts:login")

    is_waiter = request.user.groups.filter(
        name__iexact="Waiter"
    ).exists()

    if not is_waiter:
        messages.error(
            request,
            "Service requests are restricted to Waiter staff.",
        )

        return redirect("home")

    from orders.models import ServiceRequest

    active_requests = (
        ServiceRequest.objects
        .filter(
            status__in=[
                "requested",
                "accepted",
            ],
            request_type__in=[
                "water",
                "cutlery",
                "bill",
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

    completed_requests = (
        ServiceRequest.objects
        .filter(
            status="completed",
            request_type__in=[
                "water",
                "cutlery",
                "bill",
            ],
        )
        .select_related(
            "session",
            "session__table",
        )
        .order_by(
            "-completed_at",
        )[:20]
    )

    requested_count = (
        ServiceRequest.objects
        .filter(
            status="requested",
            request_type__in=[
                "water",
                "cutlery",
                "bill",
            ],
        )
        .count()
    )

    accepted_count = (
        ServiceRequest.objects
        .filter(
            status="accepted",
            request_type__in=[
                "water",
                "cutlery",
                "bill",
            ],
        )
        .count()
    )

    completed_count = (
        ServiceRequest.objects
        .filter(
            status="completed",
            request_type__in=[
                "water",
                "cutlery",
                "bill",
            ],
        )
        .count()
    )

    return render(
        request,
        "kitchen/service_requests.html",
        {
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
@transaction.atomic
def accept_service_request(request, request_id):
    """
    Allow one Waiter to claim a customer service request.

    Only water, cutlery and bill requests belong to the
    Waiter workflow.

    select_for_update() prevents two Waiters from accepting
    the same request simultaneously.
    """

    if not request.user.is_authenticated:
        return redirect("accounts:login")

    is_waiter = request.user.groups.filter(
        name__iexact="Waiter"
    ).exists()

    if not is_waiter:
        messages.error(
            request,
            "Only Waiter staff can accept service requests.",
        )

        return redirect("home")

    if request.method != "POST":
        return redirect(
            "kitchen:service_requests"
        )

    from orders.models import ServiceRequest

    service_request = get_object_or_404(
        ServiceRequest.objects
        .select_for_update()
        .select_related(
            "session",
            "session__table",
        ),
        id=request_id,
        request_type__in=[
            "water",
            "cutlery",
            "bill",
        ],
    )

    if service_request.status != "requested":
        messages.warning(
            request,
            (
                "This service request has already "
                "been accepted or completed."
            ),
        )

        return redirect(
            "kitchen:service_requests"
        )

    service_request.status = "accepted"

    service_request.save(
        update_fields=[
            "status",
        ],
    )

    messages.success(
        request,
        (
            f"Service request for Table "
            f"{service_request.session.table.table_number} "
            "has been assigned to you."
        ),
    )

    return redirect(
        "kitchen:service_requests"
    )


# ============================================================
# COMPLETE SERVICE REQUEST
# ============================================================

@login_required
@transaction.atomic
def complete_service_request(request, request_id):
    """
    Mark an accepted Waiter service request as completed.
    """

    if not request.user.is_authenticated:
        return redirect("accounts:login")

    is_waiter = request.user.groups.filter(
        name__iexact="Waiter"
    ).exists()

    if not is_waiter:
        messages.error(
            request,
            "Only Waiter staff can complete service requests.",
        )

        return redirect("home")

    if request.method != "POST":
        return redirect(
            "kitchen:service_requests"
        )

    from orders.models import ServiceRequest

    service_request = get_object_or_404(
        ServiceRequest.objects
        .select_for_update()
        .select_related(
            "session",
            "session__table",
        ),
        id=request_id,
        request_type__in=[
            "water",
            "cutlery",
            "bill",
        ],
    )

    if service_request.status != "accepted":
        messages.warning(
            request,
            (
                "Only an accepted service request "
                "can be completed."
            ),
        )

        return redirect(
            "kitchen:service_requests"
        )

    service_request.status = "completed"
    service_request.completed_at = timezone.now()

    service_request.save(
        update_fields=[
            "status",
            "completed_at",
        ],
    )

    messages.success(
        request,
        (
            f"Service request for Table "
            f"{service_request.session.table.table_number} "
            "has been completed."
        ),
    )

    return redirect(
        "kitchen:service_requests"
    )