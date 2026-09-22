from decimal import Decimal

from django.core.management.base import BaseCommand

from inventory.models import Ingredient, MenuIngredient
from restaurant.models import MenuItem


INVENTORY_ITEMS = [
    (
        "Basmati Rice",
        "kg",
        "25.000",
        "8.000",
    ),
    (
        "Chicken Breast",
        "kg",
        "15.000",
        "5.000",
    ),
    (
        "Paneer",
        "kg",
        "10.000",
        "3.000",
    ),
    (
        "Fresh Tomatoes",
        "kg",
        "20.000",
        "6.000",
    ),
    (
        "Onions",
        "kg",
        "25.000",
        "7.000",
    ),
    (
        "Potatoes",
        "kg",
        "20.000",
        "6.000",
    ),
    (
        "Cooking Oil",
        "l",
        "30.000",
        "10.000",
    ),
    (
        "Butter",
        "kg",
        "8.000",
        "3.000",
    ),
    (
        "Cream",
        "l",
        "10.000",
        "3.000",
    ),
    (
        "Parmesan Cheese",
        "kg",
        "5.000",
        "2.000",
    ),
    (
        "Mozzarella",
        "kg",
        "8.000",
        "3.000",
    ),
    (
        "Prawns",
        "kg",
        "7.000",
        "2.000",
    ),
    (
        "Salmon",
        "kg",
        "6.000",
        "2.000",
    ),
    (
        "Flour",
        "kg",
        "20.000",
        "6.000",
    ),
    (
        "Sugar",
        "kg",
        "15.000",
        "5.000",
    ),
    (
        "Coffee Beans",
        "kg",
        "8.000",
        "2.000",
    ),
    (
        "Green Tea",
        "kg",
        "4.000",
        "1.000",
    ),
    (
        "Mango",
        "kg",
        "12.000",
        "4.000",
    ),
]


def recipe_for_menu_item(menu_name):
    name = menu_name.lower()

    recipe = {}

    # ---------------------------------------------------------
    # PROTEINS
    # ---------------------------------------------------------

    if "chicken" in name:
        recipe["Chicken Breast"] = Decimal("0.180")

    if "prawn" in name:
        recipe["Prawns"] = Decimal("0.150")

    if "salmon" in name:
        recipe["Salmon"] = Decimal("0.120")

    # ---------------------------------------------------------
    # DAIRY
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # RICE
    # ---------------------------------------------------------

    if "biryani" in name:
        recipe["Basmati Rice"] = Decimal("0.180")

    # ---------------------------------------------------------
    # VEGETABLES
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # FLOUR
    # ---------------------------------------------------------

    if any(
        word in name
        for word in [
            "pizza",
            "pasta",
            "ravioli",
            "tagliatelle",
            "tacos",
            "enchiladas",
            "quesadilla",
        ]
    ):
        recipe["Flour"] = Decimal("0.120")

    # ---------------------------------------------------------
    # OIL
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # COFFEE
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # TEA
    # ---------------------------------------------------------

    if any(
        word in name
        for word in [
            "tea",
            "matcha",
        ]
    ):
        recipe["Green Tea"] = Decimal("0.004")

    # ---------------------------------------------------------
    # SUGAR
    # ---------------------------------------------------------

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


class Command(BaseCommand):

    help = (
        "Create/update IDDS inventory and recipe data."
    )

    def handle(self, *args, **options):

        created_count = 0
        updated_count = 0
        recipe_created = 0
        recipe_updated = 0

        # =====================================================
        # INVENTORY
        # =====================================================

        for (
            name,
            unit,
            current_stock,
            reorder_level,
        ) in INVENTORY_ITEMS:

            ingredient, created = (
                Ingredient.objects.get_or_create(
                    name=name,
                    defaults={
                        "unit": unit,
                        "current_stock": Decimal(
                            current_stock
                        ),
                        "minimum_stock": Decimal(
                            reorder_level
                        ),
                        "reorder_level": Decimal(
                            reorder_level
                        ),
                        "cost_per_unit": Decimal(
                            "0.00"
                        ),
                        "supplier_name": (
                            "IDDS Demo Supplier"
                        ),
                        "is_active": True,
                    },
                )
            )

            if created:
                created_count += 1
                continue

            ingredient.unit = unit
            ingredient.current_stock = Decimal(
                current_stock
            )
            ingredient.minimum_stock = Decimal(
                reorder_level
            )
            ingredient.reorder_level = Decimal(
                reorder_level
            )
            ingredient.is_active = True

            ingredient.save(
                update_fields=[
                    "unit",
                    "current_stock",
                    "minimum_stock",
                    "reorder_level",
                    "is_active",
                    "updated_at",
                ]
            )

            updated_count += 1

        # =====================================================
        # INGREDIENT MAP
        # =====================================================

        ingredient_map = {
            ingredient.name: ingredient
            for ingredient in Ingredient.objects.filter(
                name__in=[
                    row[0]
                    for row in INVENTORY_ITEMS
                ]
            )
        }

        # =====================================================
        # ACTIVE MENU RECIPES
        # =====================================================

        active_menu_items = (
            MenuItem.objects
            .filter(is_available=True)
            .order_by("id")
        )

        active_menu_item_ids = set()

        for menu_item in active_menu_items:

            active_menu_item_ids.add(
                menu_item.id
            )

            recipe = recipe_for_menu_item(
                menu_item.name
            )

            recipe_ingredient_ids = set()

            for (
                ingredient_name,
                quantity_required,
            ) in recipe.items():

                ingredient = ingredient_map.get(
                    ingredient_name
                )

                if ingredient is None:
                    continue

                recipe_ingredient_ids.add(
                    ingredient.id
                )

                _, created = (
                    MenuIngredient.objects
                    .update_or_create(
                        menu_item_id=menu_item.id,
                        ingredient=ingredient,
                        defaults={
                            "quantity_required":
                                quantity_required,
                        },
                    )
                )

                if created:
                    recipe_created += 1
                else:
                    recipe_updated += 1

            # Remove stale ingredient links from this active
            # menu item when the recipe definition no longer
            # contains them.
            stale_links = (
                MenuIngredient.objects
                .filter(
                    menu_item_id=menu_item.id
                )
            )

            if recipe_ingredient_ids:
                stale_links = stale_links.exclude(
                    ingredient_id__in=recipe_ingredient_ids
                )

            stale_links.delete()

        # =====================================================
        # REMOVE RECIPE LINKS FROM INACTIVE OLD MENU ITEMS
        # =====================================================

        stale_menu_ingredients = (
            MenuIngredient.objects
            .exclude(
                menu_item_id__in=active_menu_item_ids
            )
        )

        stale_recipe_count = (
            stale_menu_ingredients.count()
        )

        stale_menu_ingredients.delete()

        # =====================================================
        # OUTPUT
        # =====================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "INVENTORY + RECIPE DATA READY"
            )
        )

        self.stdout.write(
            f"Ingredients created: {created_count}"
        )

        self.stdout.write(
            f"Ingredients updated: {updated_count}"
        )

        self.stdout.write(
            f"Recipe rows created: {recipe_created}"
        )

        self.stdout.write(
            f"Recipe rows updated: {recipe_updated}"
        )

        self.stdout.write(
            f"Stale recipe rows removed: "
            f"{stale_recipe_count}"
        )

        self.stdout.write(
            "Active menu items with recipes: "
            f"{len(active_menu_item_ids)}"
        )

        self.stdout.write(
            "Total recipe rows: "
            f"{MenuIngredient.objects.count()}"
        )

        self.stdout.write(
            "Total ingredients: "
            f"{Ingredient.objects.count()}"
        )

        self.stdout.write("")

        self.stdout.write(
            self.style.WARNING(
                "Inventory is deducted when a Chef starts "
                "preparing an order."
            )
        )