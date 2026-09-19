from decimal import Decimal

from django.db import transaction

from .models import Ingredient, StockMovement


# ============================================================
# DEMO RECIPE RULES
# ============================================================
#
# Quantities are per ONE menu item.
#
# These values are intentionally realistic demo quantities,
# not production recipe specifications.
# ============================================================

def _recipe_for_menu_item(menu_name):
    name = menu_name.lower()

    recipe = {}

    # --------------------------------------------------------
    # MAIN PROTEINS
    # --------------------------------------------------------

    if "chicken" in name:
        recipe["Chicken Breast"] = Decimal("0.180")

    if "prawn" in name:
        recipe["Prawns"] = Decimal("0.150")

    if "salmon" in name:
        recipe["Salmon"] = Decimal("0.120")

    # --------------------------------------------------------
    # PANEER / DAIRY
    # --------------------------------------------------------

    if "paneer" in name:
        recipe["Paneer"] = Decimal("0.150")

    if "butter" in name:
        recipe["Butter"] = Decimal("0.020")

    if (
        "cream" in name
        or "panna cotta" in name
        or "crème brûlée" in name
    ):
        recipe["Cream"] = Decimal("0.030")

    if (
        "parmesan" in name
        or "caesar" in name
    ):
        recipe["Parmesan Cheese"] = Decimal("0.020")

    if (
        "pizza" in name
        or "cheese" in name
    ):
        recipe["Mozzarella"] = Decimal("0.080")

    # --------------------------------------------------------
    # RICE / GRAINS
    # --------------------------------------------------------

    if "biryani" in name:
        recipe["Basmati Rice"] = Decimal("0.180")

    # --------------------------------------------------------
    # PRODUCE
    # --------------------------------------------------------

    if (
        "tomato" in name
        or "arrabbiata" in name
        or "margherita" in name
        or "butter chicken" in name
    ):
        recipe["Fresh Tomatoes"] = Decimal("0.080")

    if (
        "onion" in name
        or "biryani" in name
        or "curry" in name
    ):
        recipe["Onions"] = Decimal("0.050")

    if "potato" in name:
        recipe["Potatoes"] = Decimal("0.120")

    if "mango" in name:
        recipe["Mango"] = Decimal("0.120")

    # --------------------------------------------------------
    # BAKERY / FLOUR
    # --------------------------------------------------------

    if (
        "pizza" in name
        or "pasta" in name
        or "ravioli" in name
        or "tagliatelle" in name
        or "tacos" in name
        or "enchiladas" in name
        or "quesadilla" in name
    ):
        recipe["Flour"] = Decimal("0.120")

    # --------------------------------------------------------
    # OIL
    # --------------------------------------------------------

    if any(
        word in name
        for word in [
            "chicken",
            "prawn",
            "pizza",
            "pasta",
            "tikka",
            "biryani",
            "tempura",
            "tacos",
        ]
    ):
        recipe["Cooking Oil"] = Decimal("0.020")

    # --------------------------------------------------------
    # COFFEE / TEA
    # --------------------------------------------------------

    if any(
        word in name
        for word in [
            "coffee",
            "cappuccino",
            "espresso",
            "latte",
        ]
    ):
        recipe["Coffee Beans"] = Decimal("0.018")

    if any(
        word in name
        for word in [
            "tea",
            "matcha",
        ]
    ):
        recipe["Green Tea"] = Decimal("0.004")

    # --------------------------------------------------------
    # SUGAR
    # --------------------------------------------------------

    if any(
        word in name
        for word in [
            "dessert",
            "cake",
            "cheesecake",
            "tiramisu",
            "tea",
            "coffee",
            "cappuccino",
        ]
    ):
        recipe["Sugar"] = Decimal("0.010")

    return recipe


# ============================================================
# ORDER INVENTORY DEDUCTION
# ============================================================

@transaction.atomic
def deduct_inventory_for_order(order):
    """
    Deduct inventory when a Chef starts preparing an order.

    This function:
        1. Calculates required ingredients.
        2. Checks stock before changing anything.
        3. Prevents negative inventory.
        4. Creates StockMovement records.
        5. Records the order number as the reference.
    """

    required = {}

    for item in order.items.all():

        recipe = _recipe_for_menu_item(
            item.item_name
        )

        for ingredient_name, quantity in recipe.items():

            total_quantity = (
                quantity * item.quantity
            )

            required[ingredient_name] = (
                required.get(
                    ingredient_name,
                    Decimal("0.000"),
                )
                + total_quantity
            )

    if not required:
        return {
            "success": True,
            "message": "No configured inventory ingredients for this order.",
            "used": [],
        }

    ingredients = {}

    for ingredient_name, quantity in required.items():

        ingredient = (
            Ingredient.objects
            .select_for_update()
            .filter(
                name=ingredient_name,
                is_active=True,
            )
            .first()
        )

        # Ingredient is not in the seeded inventory.
        # Skip it rather than blocking the order.
        if ingredient is None:
            continue

        ingredients[ingredient_name] = ingredient

        if ingredient.current_stock < quantity:

            return {
                "success": False,
                "message": (
                    f"Not enough {ingredient.name}. "
                    f"Required: {quantity} {ingredient.unit}. "
                    f"Available: {ingredient.current_stock} "
                    f"{ingredient.unit}."
                ),
                "used": [],
            }

    used = []

    for ingredient_name, quantity in required.items():

        ingredient = ingredients.get(
            ingredient_name
        )

        if ingredient is None:
            continue

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
            reference=f"Order #{order.id}",
            notes=(
                f"Automatic kitchen usage for "
                f"Order #{order.id}."
            ),
        )

        used.append(
            {
                "ingredient": ingredient.name,
                "quantity": quantity,
                "unit": ingredient.unit,
            }
        )

    return {
        "success": True,
        "message": "Inventory updated successfully.",
        "used": used,
    }