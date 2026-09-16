from decimal import Decimal

from django.db import migrations


def create_restaurant_data(apps, schema_editor):
    DiningTable = apps.get_model("restaurant", "DiningTable")
    MenuCategory = apps.get_model("restaurant", "MenuCategory")
    MenuItem = apps.get_model("restaurant", "MenuItem")

    # ---------------------------------------------------------
    # RESTAURANT TABLES
    # ---------------------------------------------------------
    tables = [
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 4),
        (5, 4),
        (6, 4),
        (7, 6),
        (8, 6),
    ]

    for table_number, capacity in tables:
        DiningTable.objects.update_or_create(
            table_number=table_number,
            defaults={
                "capacity": capacity,
                "status": "available",
            },
        )

    # ---------------------------------------------------------
    # MENU CATEGORIES
    # ---------------------------------------------------------
    categories = {
        "Coffee": (
            "Freshly prepared coffee crafted for every mood."
        ),
        "Breakfast": (
            "Comforting breakfast favourites prepared fresh."
        ),
        "Main Course": (
            "Hearty dishes prepared for a satisfying meal."
        ),
    }

    category_objects = {}

    for name, description in categories.items():
        category, _ = MenuCategory.objects.update_or_create(
            name=name,
            defaults={
                "description": description,
            },
        )
        category_objects[name] = category

    # ---------------------------------------------------------
    # MENU ITEMS
    # ---------------------------------------------------------
    menu_items = [
        {
            "category": "Coffee",
            "name": "Classic Cappuccino",
            "description": (
                "Rich espresso topped with silky steamed milk "
                "and delicate foam."
            ),
            "price": Decimal("180.00"),
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1495474472287-4d71bcdd2085"
                "?auto=format&fit=crop&w=900&q=85"
            ),
        },
        {
            "category": "Coffee",
            "name": "Caramel Latte",
            "description": (
                "Smooth espresso, steamed milk and "
                "a gentle caramel finish."
            ),
            "price": Decimal("210.00"),
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1572442388796-11668a67e53d"
                "?auto=format&fit=crop&w=900&q=85"
            ),
        },
        {
            "category": "Coffee",
            "name": "Cold Brew",
            "description": (
                "Slow-steeped coffee served chilled "
                "for a smooth, refreshing finish."
            ),
            "price": Decimal("190.00"),
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1517701604599-bb29b565090c"
                "?auto=format&fit=crop&w=900&q=85"
            ),
        },
        {
            "category": "Breakfast",
            "name": "Avocado Toast",
            "description": (
                "Toasted artisan bread topped with creamy "
                "avocado and fresh herbs."
            ),
            "price": Decimal("280.00"),
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1541519227354-08fa5d50c44d"
                "?auto=format&fit=crop&w=900&q=85"
            ),
        },
        {
            "category": "Breakfast",
            "name": "Classic Pancakes",
            "description": (
                "Fluffy pancakes served with fresh fruit "
                "and a drizzle of syrup."
            ),
            "price": Decimal("260.00"),
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1528207776546-365bb710ee93"
                "?auto=format&fit=crop&w=900&q=85"
            ),
        },
        {
            "category": "Main Course",
            "name": "Creamy Alfredo Pasta",
            "description": (
                "Creamy parmesan sauce tossed with "
                "perfectly cooked pasta."
            ),
            "price": Decimal("360.00"),
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1551183053-bf91a1d81141"
                "?auto=format&fit=crop&w=900&q=85"
            ),
        },
        {
            "category": "Main Course",
            "name": "Grilled Herb Chicken",
            "description": (
                "Juicy grilled chicken seasoned with herbs "
                "and served with fresh vegetables."
            ),
            "price": Decimal("420.00"),
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1532550907401-a500c9a57435"
                "?auto=format&fit=crop&w=900&q=85"
            ),
        },
    ]

    for item in menu_items:
        MenuItem.objects.update_or_create(
            name=item["name"],
            category=category_objects[item["category"]],
            defaults={
                "description": item["description"],
                "price": item["price"],
                "is_available": True,
                "image_url": item["image_url"],
            },
        )


def remove_restaurant_data(apps, schema_editor):
    MenuItem = apps.get_model("restaurant", "MenuItem")
    MenuCategory = apps.get_model("restaurant", "MenuCategory")

    item_names = [
        "Classic Cappuccino",
        "Caramel Latte",
        "Cold Brew",
        "Avocado Toast",
        "Classic Pancakes",
        "Creamy Alfredo Pasta",
        "Grilled Herb Chicken",
    ]

    MenuItem.objects.filter(name__in=item_names).delete()

    category_names = [
        "Coffee",
        "Breakfast",
        "Main Course",
    ]

    for category_name in category_names:
        category = MenuCategory.objects.filter(
            name=category_name
        ).first()

        if category and not category.items.exists():
            category.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("restaurant", "0002_menuitem_image_url"),
    ]

    operations = [
        migrations.RunPython(
            create_restaurant_data,
            remove_restaurant_data,
        ),
    ]