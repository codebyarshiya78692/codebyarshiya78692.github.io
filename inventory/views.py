from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import Ingredient, StockMovement


def _parse_quantity(value):
    """
    Convert a submitted quantity into Decimal.

    Returning None makes validation easier for all stock
    movement actions.
    """

    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError):
        return None


def _staff_required(request):
    """
    Inventory is a management-only area.

    Only the Admin/superuser can view or modify inventory.
    Chef and Waiter users must not access it.
    """

    return (
        request.user.is_authenticated
        and request.user.is_superuser
    )


def _dashboard_redirect():
    """
    Keep all inventory actions returning to the same dashboard.
    """

    return redirect("inventory:dashboard")


@login_required
def dashboard(request):
    """
    Staff inventory dashboard.

    Displays:
        - Active ingredients
        - Current stock
        - Low-stock ingredients
        - Total stock value
        - Recent stock movements
    """

    if not _staff_required(request):
        return render(
            request,
            "inventory/dashboard.html",
            {
                "access_denied": True,
            },
        )

    ingredients = (
        Ingredient.objects
        .filter(is_active=True)
        .order_by("name")
    )

    low_stock = [
        ingredient
        for ingredient in ingredients
        if ingredient.is_low_stock
    ]

    movements = (
        StockMovement.objects
        .select_related("ingredient")
        .order_by("-created_at")[:20]
    )

    total_ingredients = ingredients.count()

    total_stock_value = sum(
        (
            ingredient.current_stock
            * ingredient.cost_per_unit
            for ingredient in ingredients
        ),
        Decimal("0.00"),
    )

    context = {
        "ingredients": ingredients,
        "low_stock": low_stock,
        "movements": movements,
        "total_ingredients": total_ingredients,
        "low_stock_count": len(low_stock),
        "total_stock_value": total_stock_value,
        "access_denied": False,
    }

    return render(
        request,
        "inventory/dashboard.html",
        context,
    )


@login_required
@transaction.atomic
def add_stock(request, ingredient_id):
    """
    Add purchased stock to an ingredient.
    """

    if not _staff_required(request):
        return _dashboard_redirect()

    if request.method != "POST":
        return _dashboard_redirect()

    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        is_active=True,
    )

    raw_quantity = request.POST.get(
        "quantity",
        "",
    ).strip()

    raw_unit_cost = request.POST.get(
        "unit_cost",
        str(ingredient.cost_per_unit),
    ).strip()

    reference = request.POST.get(
        "reference",
        "",
    ).strip()

    notes = request.POST.get(
        "notes",
        "",
    ).strip()

    quantity = _parse_quantity(raw_quantity)
    unit_cost = _parse_quantity(raw_unit_cost)

    if quantity is None or unit_cost is None:
        messages.error(
            request,
            "Please enter valid stock quantity and unit cost.",
        )
        return _dashboard_redirect()

    if quantity <= 0:
        messages.error(
            request,
            "Stock quantity must be greater than zero.",
        )
        return _dashboard_redirect()

    if unit_cost < 0:
        messages.error(
            request,
            "Unit cost cannot be negative.",
        )
        return _dashboard_redirect()

    ingredient.current_stock += quantity

    if unit_cost > 0:
        ingredient.cost_per_unit = unit_cost

    ingredient.save(
        update_fields=[
            "current_stock",
            "cost_per_unit",
            "updated_at",
        ]
    )

    StockMovement.objects.create(
        ingredient=ingredient,
        movement_type="purchase",
        quantity=quantity,
        unit_cost=unit_cost,
        reference=reference or "Stock purchase",
        notes=notes,
    )

    messages.success(
        request,
        (
            f"{ingredient.name}: "
            f"{quantity} {ingredient.unit} added to stock."
        ),
    )

    return _dashboard_redirect()


@login_required
@transaction.atomic
def adjust_stock(request, ingredient_id):
    """
    Manually set an ingredient's stock level.
    """

    if not _staff_required(request):
        return _dashboard_redirect()

    if request.method != "POST":
        return _dashboard_redirect()

    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        is_active=True,
    )

    raw_stock = request.POST.get(
        "current_stock",
        "",
    ).strip()

    notes = request.POST.get(
        "notes",
        "",
    ).strip()

    new_stock = _parse_quantity(raw_stock)

    if new_stock is None:
        messages.error(
            request,
            "Please enter a valid stock value.",
        )
        return _dashboard_redirect()

    if new_stock < 0:
        messages.error(
            request,
            "Stock cannot be negative.",
        )
        return _dashboard_redirect()

    old_stock = ingredient.current_stock
    difference = new_stock - old_stock

    ingredient.current_stock = new_stock

    ingredient.save(
        update_fields=[
            "current_stock",
            "updated_at",
        ]
    )

    StockMovement.objects.create(
        ingredient=ingredient,
        movement_type="adjustment",
        quantity=abs(difference),
        unit_cost=ingredient.cost_per_unit,
        reference="Manual stock adjustment",
        notes=notes or (
            f"Stock changed from "
            f"{old_stock} to {new_stock}."
        ),
    )

    messages.success(
        request,
        f"{ingredient.name} stock updated successfully.",
    )

    return _dashboard_redirect()


@login_required
@transaction.atomic
def use_stock(request, ingredient_id):
    """
    Record ingredient stock used during restaurant operations.

    Usage reduces current stock and creates a usage movement.
    """

    if not _staff_required(request):
        return _dashboard_redirect()

    if request.method != "POST":
        return _dashboard_redirect()

    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        is_active=True,
    )

    raw_quantity = request.POST.get(
        "quantity",
        "",
    ).strip()

    reference = request.POST.get(
        "reference",
        "",
    ).strip()

    notes = request.POST.get(
        "notes",
        "",
    ).strip()

    quantity = _parse_quantity(raw_quantity)

    if quantity is None or quantity <= 0:
        messages.error(
            request,
            "Usage quantity must be greater than zero.",
        )
        return _dashboard_redirect()

    if quantity > ingredient.current_stock:
        messages.error(
            request,
            (
                f"Insufficient stock for {ingredient.name}. "
                f"Available: {ingredient.current_stock} "
                f"{ingredient.unit}."
            ),
        )
        return _dashboard_redirect()

    ingredient.current_stock -= quantity

    ingredient.save(
        update_fields=[
            "current_stock",
            "updated_at",
        ]
    )

    StockMovement.objects.create(
        ingredient=ingredient,
        movement_type="usage",
        quantity=quantity,
        unit_cost=ingredient.cost_per_unit,
        reference=reference or "Restaurant usage",
        notes=notes,
    )

    messages.success(
        request,
        (
            f"{ingredient.name}: "
            f"{quantity} {ingredient.unit} recorded as used."
        ),
    )

    return _dashboard_redirect()


@login_required
@transaction.atomic
def record_waste(request, ingredient_id):
    """
    Record wasted ingredient stock.

    Waste reduces current stock and is permanently recorded
    as a stock movement for reporting and audit purposes.
    """

    if not _staff_required(request):
        return _dashboard_redirect()

    if request.method != "POST":
        return _dashboard_redirect()

    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        is_active=True,
    )

    raw_quantity = request.POST.get(
        "quantity",
        "",
    ).strip()

    reference = request.POST.get(
        "reference",
        "",
    ).strip()

    notes = request.POST.get(
        "notes",
        "",
    ).strip()

    quantity = _parse_quantity(raw_quantity)

    if quantity is None or quantity <= 0:
        messages.error(
            request,
            "Waste quantity must be greater than zero.",
        )
        return _dashboard_redirect()

    if quantity > ingredient.current_stock:
        messages.error(
            request,
            (
                f"Cannot record more waste than available stock "
                f"for {ingredient.name}."
            ),
        )
        return _dashboard_redirect()

    ingredient.current_stock -= quantity

    ingredient.save(
        update_fields=[
            "current_stock",
            "updated_at",
        ]
    )

    StockMovement.objects.create(
        ingredient=ingredient,
        movement_type="waste",
        quantity=quantity,
        unit_cost=ingredient.cost_per_unit,
        reference=reference or "Stock waste",
        notes=notes,
    )

    messages.success(
        request,
        (
            f"{ingredient.name}: "
            f"{quantity} {ingredient.unit} recorded as waste."
        ),
    )

    return _dashboard_redirect()


@login_required
@transaction.atomic
def return_stock(request, ingredient_id):
    """
    Record stock returned by a supplier or received back
    into inventory.

    A return movement increases the available stock.
    """

    if not _staff_required(request):
        return _dashboard_redirect()

    if request.method != "POST":
        return _dashboard_redirect()

    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        is_active=True,
    )

    raw_quantity = request.POST.get(
        "quantity",
        "",
    ).strip()

    raw_unit_cost = request.POST.get(
        "unit_cost",
        str(ingredient.cost_per_unit),
    ).strip()

    reference = request.POST.get(
        "reference",
        "",
    ).strip()

    notes = request.POST.get(
        "notes",
        "",
    ).strip()

    quantity = _parse_quantity(raw_quantity)
    unit_cost = _parse_quantity(raw_unit_cost)

    if quantity is None or unit_cost is None:
        messages.error(
            request,
            "Please enter valid return quantity and unit cost.",
        )
        return _dashboard_redirect()

    if quantity <= 0:
        messages.error(
            request,
            "Return quantity must be greater than zero.",
        )
        return _dashboard_redirect()

    if unit_cost < 0:
        messages.error(
            request,
            "Unit cost cannot be negative.",
        )
        return _dashboard_redirect()

    ingredient.current_stock += quantity

    if unit_cost > 0:
        ingredient.cost_per_unit = unit_cost

    ingredient.save(
        update_fields=[
            "current_stock",
            "cost_per_unit",
            "updated_at",
        ]
    )

    StockMovement.objects.create(
        ingredient=ingredient,
        movement_type="return",
        quantity=quantity,
        unit_cost=unit_cost,
        reference=reference or "Stock return",
        notes=notes,
    )

    messages.success(
        request,
        (
            f"{ingredient.name}: "
            f"{quantity} {ingredient.unit} returned to stock."
        ),
    )

    return _dashboard_redirect()


@login_required
def stock_movement_history(request, ingredient_id):
    """
    Show the complete movement history for one ingredient.

    This is useful for stock auditing and demonstration of the
    inventory traceability feature.
    """

    if not _staff_required(request):
        return _dashboard_redirect()

    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        is_active=True,
    )

    movements = (
        StockMovement.objects
        .filter(ingredient=ingredient)
        .order_by("-created_at")
    )

    return render(
        request,
        "inventory/movement_history.html",
        {
            "ingredient": ingredient,
            "movements": movements,
        },
    )