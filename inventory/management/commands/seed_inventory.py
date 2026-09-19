from decimal import Decimal

from django.core.management.base import BaseCommand

from inventory.models import Ingredient


INVENTORY_ITEMS = [
    ("Basmati Rice", "kg", "25", "8"),
    ("Chicken Breast", "kg", "15", "5"),
    ("Paneer", "kg", "10", "3"),
    ("Fresh Tomatoes", "kg", "20", "6"),
    ("Onions", "kg", "25", "7"),
    ("Potatoes", "kg", "20", "6"),
    ("Cooking Oil", "litre", "30", "10"),
    ("Butter", "kg", "8", "3"),
    ("Cream", "litre", "10", "3"),
    ("Parmesan Cheese", "kg", "5", "2"),
    ("Mozzarella", "kg", "8", "3"),
    ("Prawns", "kg", "7", "2"),
    ("Salmon", "kg", "6", "2"),
    ("Flour", "kg", "20", "6"),
    ("Sugar", "kg", "15", "5"),
    ("Coffee Beans", "kg", "8", "3"),
    ("Green Tea", "kg", "4", "1"),
    ("Mango", "kg", "12", "4"),
]


class Command(BaseCommand):
    help = "Create or update demo inventory ingredients for IDDS."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for name, unit, current_stock, reorder_level in INVENTORY_ITEMS:
            ingredient, created = Ingredient.objects.get_or_create(
                name=name,
                defaults={
                    "unit": unit,
                    "current_stock": Decimal(current_stock),
                    "minimum_stock": Decimal(reorder_level),
                    "reorder_level": Decimal(reorder_level),
                    "cost_per_unit": Decimal("0.00"),
                    "supplier_name": "IDDS Demo Supplier",
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                ingredient.unit = unit
                ingredient.current_stock = Decimal(current_stock)
                ingredient.minimum_stock = Decimal(reorder_level)
                ingredient.reorder_level = Decimal(reorder_level)
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

        self.stdout.write(self.style.SUCCESS("INVENTORY DEMO DATA READY"))
        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Updated: {updated_count}")
        self.stdout.write(f"Total ingredients: {Ingredient.objects.count()}")