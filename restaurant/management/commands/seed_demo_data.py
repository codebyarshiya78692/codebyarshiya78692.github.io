from decimal import Decimal

from django.core.management.base import BaseCommand

from restaurant.models import DiningTable, MenuCategory, MenuItem


class Command(BaseCommand):
    help = "Create the standard IDDS demo tables and menu data."

    TABLES = [
        {"table_number": 1, "capacity": 2},
        {"table_number": 2, "capacity": 2},
        {"table_number": 3, "capacity": 2},
        {"table_number": 4, "capacity": 4},
        {"table_number": 5, "capacity": 4},
        {"table_number": 6, "capacity": 4},
        {"table_number": 7, "capacity": 6},
        {"table_number": 8, "capacity": 8},
    ]

    CATEGORIES = [
        {
            "name": "Coffee & Beverages",
            "description": "Freshly brewed coffee, tea and refreshing beverages.",
        },
        {
            "name": "Breakfast & Bites",
            "description": "Comforting breakfast plates and light café bites.",
        },
        {
            "name": "Main Plates",
            "description": "Freshly prepared signature dishes from our kitchen.",
        },
    ]

    MENU_ITEMS = [
        {
            "category": "Coffee & Beverages",
            "name": "Classic Cappuccino",
            "description": "Espresso with silky steamed milk and a light foam finish.",
            "price": Decimal("180.00"),
        },
        {
            "category": "Coffee & Beverages",
            "name": "Caramel Latte",
            "description": "Smooth espresso, steamed milk and caramel sweetness.",
            "price": Decimal("210.00"),
        },
        {
            "category": "Coffee & Beverages",
            "name": "Cold Brew",
            "description": "Slow-steeped coffee served chilled over ice.",
            "price": Decimal("190.00"),
        },
        {
            "category": "Breakfast & Bites",
            "name": "Avocado Toast",
            "description": "Toasted sourdough topped with creamy avocado and herbs.",
            "price": Decimal("280.00"),
        },
        {
            "category": "Breakfast & Bites",
            "name": "Classic Pancakes",
            "description": "Fluffy pancakes served with maple syrup and seasonal fruit.",
            "price": Decimal("260.00"),
        },
        {
            "category": "Main Plates",
            "name": "Creamy Alfredo Pasta",
            "description": "House pasta tossed in a creamy parmesan sauce.",
            "price": Decimal("360.00"),
        },
        {
            "category": "Main Plates",
            "name": "Grilled Herb Chicken",
            "description": "Tender grilled chicken with herbs, vegetables and house sauce.",
            "price": Decimal("420.00"),
        },
    ]

    def handle(self, *args, **options):
        created_tables = 0
        created_categories = 0
        created_items = 0

        # Tables
        for table_data in self.TABLES:
            table, created = DiningTable.objects.get_or_create(
                table_number=table_data["table_number"],
                defaults={
                    "capacity": table_data["capacity"],
                    "status": "available",
                },
            )

            if created:
                created_tables += 1
            elif table.capacity != table_data["capacity"]:
                table.capacity = table_data["capacity"]
                table.save(update_fields=["capacity"])

        # Categories
        categories = {}

        for category_data in self.CATEGORIES:
            category, created = MenuCategory.objects.get_or_create(
                name=category_data["name"],
                defaults={
                    "description": category_data["description"],
                },
            )

            if created:
                created_categories += 1
            elif category.description != category_data["description"]:
                category.description = category_data["description"]
                category.save(update_fields=["description"])

            categories[category.name] = category

        # Menu items
        for item_data in self.MENU_ITEMS:
            category = categories[item_data["category"]]

            item, created = MenuItem.objects.get_or_create(
                category=category,
                name=item_data["name"],
                defaults={
                    "description": item_data["description"],
                    "price": item_data["price"],
                    "is_available": True,
                },
            )

            if created:
                created_items += 1
            else:
                changed = False

                if item.description != item_data["description"]:
                    item.description = item_data["description"]
                    changed = True

                if item.price != item_data["price"]:
                    item.price = item_data["price"]
                    changed = True

                if not item.is_available:
                    item.is_available = True
                    changed = True

                if changed:
                    item.save(
                        update_fields=[
                            "description",
                            "price",
                            "is_available",
                        ]
                    )

        self.stdout.write(self.style.SUCCESS("IDDS demo data is ready."))
        self.stdout.write(
            f"Tables created: {created_tables} | "
            f"Categories created: {created_categories} | "
            f"Menu items created: {created_items}"
        )