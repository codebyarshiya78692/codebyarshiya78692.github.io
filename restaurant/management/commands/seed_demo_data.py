from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from restaurant.models import DiningTable, MenuCategory, MenuItem


class Command(BaseCommand):
    help = "Create the standard IDDS restaurant tables and international menu data."

    TABLES = [
        {"table_number": 1, "capacity": 2},
        {"table_number": 2, "capacity": 2},
        {"table_number": 3, "capacity": 2},
        {"table_number": 4, "capacity": 4},
        {"table_number": 5, "capacity": 4},
        {"table_number": 6, "capacity": 4},
        {"table_number": 7, "capacity": 6},
        {"table_number": 8, "capacity": 8},
        {"table_number": 9, "capacity": 4},
        {"table_number": 10, "capacity": 6},
    ]

    CATEGORIES = [
        {
            "name": "Starters",
            "description": (
                "Elegant international appetizers and small plates "
                "prepared fresh for the perfect beginning."
            ),
        },
        {
            "name": "Soups & Salads",
            "description": (
                "Fresh soups and salads inspired by flavours from around "
                "the world."
            ),
        },
        {
            "name": "Indian Specialties",
            "description": (
                "Classic Indian favourites prepared with aromatic spices "
                "and authentic flavours."
            ),
        },
        {
            "name": "International Mains",
            "description": (
                "Signature international dishes prepared fresh by our "
                "kitchen."
            ),
        },
        {
            "name": "Pizza & Pasta",
            "description": (
                "Italian-inspired pizzas, pasta and handcrafted comfort "
                "dishes."
            ),
        },
        {
            "name": "Asian & Japanese",
            "description": (
                "Popular Asian and Japanese dishes featuring bold, balanced "
                "flavours."
            ),
        },
        {
            "name": "Desserts",
            "description": (
                "Elegant desserts and indulgent sweet creations to finish "
                "your meal."
            ),
        },
        {
            "name": "Coffee & Beverages",
            "description": (
                "Coffee, tea and refreshing fruit-based beverages."
            ),
        },
    ]

    MENU_ITEMS = [
        # ========================================================
        # STARTERS
        # ========================================================

        {
            "category": "Starters",
            "name": "Burrata with Heirloom Tomatoes",
            "image": "burrata_with_heirloom_tomatoes.jpg",
            "description": (
                "Creamy burrata served with heirloom tomatoes, fresh herbs "
                "and a delicate dressing."
            ),
            "price": Decimal("420.00"),
        },
        {
            "category": "Starters",
            "name": "Truffle Parmesan Arancini",
            "image": "truffle_parmesan_arancini.jpg",
            "description": (
                "Crispy Italian rice croquettes filled with parmesan and "
                "finished with aromatic truffle."
            ),
            "price": Decimal("380.00"),
        },
        {
            "category": "Starters",
            "name": "Crispy Prawn Tempura",
            "image": "crispy_prawn_tempura.jpg",
            "description": (
                "Lightly battered prawns fried until crisp and served with "
                "a delicate dipping sauce."
            ),
            "price": Decimal("460.00"),
        },
        {
            "category": "Starters",
            "name": "Tuna Tartare with Avocado",
            "image": "tuna_tartare_with_avocado.jpg",
            "description": (
                "Fresh tuna tartare paired with creamy avocado and a "
                "lightly seasoned dressing."
            ),
            "price": Decimal("520.00"),
        },
        {
            "category": "Starters",
            "name": "Vegetable Quesadilla",
            "image": "vegetable_quesadilla.jpg",
            "description": (
                "Grilled tortilla filled with seasoned vegetables and "
                "melted cheese."
            ),
            "price": Decimal("280.00"),
        },
        {
            "category": "Starters",
            "name": "Mexican Corn with Chipotle Mayo",
            "image": "mexican_corn_with_chipotle_mayo.jpg",
            "description": (
                "Grilled sweet corn finished with smoky chipotle mayonnaise "
                "and fresh herbs."
            ),
            "price": Decimal("240.00"),
        },

        # ========================================================
        # SOUPS & SALADS
        # ========================================================

        {
            "category": "Soups & Salads",
            "name": "Classic Caesar Salad",
            "image": "classic_caesar_salad.jpg",
            "description": (
                "Crisp lettuce, parmesan and golden croutons tossed in "
                "classic Caesar dressing."
            ),
            "price": Decimal("320.00"),
        },
        {
            "category": "Soups & Salads",
            "name": "Creamy Wild Mushroom Soup",
            "image": "creamy_wild_mushroom_soup.jpg",
            "description": (
                "Rich creamy soup made with wild mushrooms and finished "
                "with fresh herbs."
            ),
            "price": Decimal("300.00"),
        },
        {
            "category": "Soups & Salads",
            "name": "French Onion Soup",
            "image": "french_onion_soup.jpg",
            "description": (
                "Slow-cooked caramelised onions in a rich broth topped with "
                "melted cheese."
            ),
            "price": Decimal("300.00"),
        },
        {
            "category": "Soups & Salads",
            "name": "Mediterranean Quinoa Salad",
            "image": "mediterranean_quinoa_salad.jpg",
            "description": (
                "Quinoa with fresh vegetables, herbs and Mediterranean "
                "flavours."
            ),
            "price": Decimal("340.00"),
        },
        {
            "category": "Soups & Salads",
            "name": "Thai Green Papaya Salad",
            "image": "thai_green_papaya_salad.jpg",
            "description": (
                "Fresh green papaya tossed with herbs, vegetables and a "
                "bright Thai dressing."
            ),
            "price": Decimal("320.00"),
        },
        {
            "category": "Soups & Salads",
            "name": "Tom Yum Prawn Soup",
            "image": "tom_yum_prawn_soup.jpg",
            "description": (
                "Aromatic Thai soup with prawns, herbs, chilli and citrus."
            ),
            "price": Decimal("380.00"),
        },

        # ========================================================
        # INDIAN SPECIALTIES
        # ========================================================

        {
            "category": "Indian Specialties",
            "name": "Butter Chicken",
            "image": "butter_chicken.jpg",
            "description": (
                "Tender chicken cooked in a rich tomato, butter and cream "
                "gravy."
            ),
            "price": Decimal("430.00"),
        },
        {
            "category": "Indian Specialties",
            "name": "Chicken Tikka",
            "image": "chicken_tikka.jpg",
            "description": (
                "Tender chicken marinated in yoghurt and aromatic spices "
                "then grilled to perfection."
            ),
            "price": Decimal("380.00"),
        },
        {
            "category": "Indian Specialties",
            "name": "Dal Makhani",
            "image": "dal_makhani.jpg",
            "description": (
                "Slow-cooked black lentils finished with butter and cream."
            ),
            "price": Decimal("280.00"),
        },
        {
            "category": "Indian Specialties",
            "name": "Hyderabadi Chicken Biryani",
            "image": "hyderabadi_chicken_biryani.jpg",
            "description": (
                "Fragrant basmati rice layered with chicken and traditional "
                "Hyderabadi biryani spices."
            ),
            "price": Decimal("450.00"),
        },
        {
            "category": "Indian Specialties",
            "name": "Lamb Rogan Josh",
            "image": "lamb_rogan_josh.jpg",
            "description": (
                "Tender lamb slow-cooked with aromatic Kashmiri spices "
                "and a rich gravy."
            ),
            "price": Decimal("520.00"),
        },
        {
            "category": "Indian Specialties",
            "name": "Paneer Tikka",
            "image": "paneer_tikka.jpg",
            "description": (
                "Char-grilled paneer marinated with yoghurt, peppers and "
                "aromatic Indian spices."
            ),
            "price": Decimal("340.00"),
        },

        # ========================================================
        # INTERNATIONAL MAINS
        # ========================================================

        {
            "category": "International Mains",
            "name": "Beef Birria Tacos",
            "image": "beef_birria_tacos.jpg",
            "description": (
                "Slow-cooked spiced beef served in crisp tortillas with "
                "fresh garnishes."
            ),
            "price": Decimal("460.00"),
        },
        {
            "category": "International Mains",
            "name": "Chicken Enchiladas",
            "image": "chicken_enchiladas.jpg",
            "description": (
                "Soft tortillas filled with seasoned chicken, topped with "
                "sauce and melted cheese."
            ),
            "price": Decimal("420.00"),
        },
        {
            "category": "International Mains",
            "name": "Chicken Tacos with Avocado Salsa",
            "image": "chicken_tacos_with_avocado_salsa.jpg",
            "description": (
                "Seasoned chicken tacos served with fresh avocado salsa "
                "and herbs."
            ),
            "price": Decimal("390.00"),
        },
        {
            "category": "International Mains",
            "name": "Chicken Yakitori",
            "image": "chicken_yakitori.jpg",
            "description": (
                "Japanese-style grilled chicken skewers glazed with a "
                "sweet savoury sauce."
            ),
            "price": Decimal("380.00"),
        },
        {
            "category": "International Mains",
            "name": "Chicken Satay with Peanut Sauce",
            "image": "chickensataywithpeanutsauce.jpg",
            "description": (
                "Grilled chicken skewers served with a rich and creamy "
                "peanut dipping sauce."
            ),
            "price": Decimal("390.00"),
        },
        {
            "category": "International Mains",
            "name": "Miso Glazed Black Cod",
            "image": "miso_glazed_black_cod.jpg",
            "description": (
                "Delicate black cod glazed with sweet savoury miso and "
                "finished with fresh herbs."
            ),
            "price": Decimal("680.00"),
        },
        {
            "category": "International Mains",
            "name": "Thai Basil Chicken",
            "image": "thai_basil_chicken.jpg",
            "description": (
                "Tender chicken stir-fried with Thai basil, chilli and "
                "aromatic seasonings."
            ),
            "price": Decimal("390.00"),
        },
        {
            "category": "International Mains",
            "name": "Thai Green Curry",
            "image": "thai_green_curry.jpg",
            "description": (
                "Aromatic Thai green curry prepared with coconut milk, "
                "herbs and vegetables."
            ),
            "price": Decimal("420.00"),
        },
        {
            "category": "International Mains",
            "name": "Thai Red Curry",
            "image": "thai_red_curry.jpg",
            "description": (
                "Rich Thai red curry with coconut milk, vegetables and "
                "fragrant spices."
            ),
            "price": Decimal("420.00"),
        },
        {
            "category": "International Mains",
            "name": "Wagyu Beef Teriyaki",
            "image": "wagyu_beef_teriyaki.jpg",
            "description": (
                "Premium wagyu beef glazed with Japanese teriyaki sauce "
                "and served with seasonal accompaniments."
            ),
            "price": Decimal("850.00"),
        },

        # ========================================================
        # PIZZA & PASTA
        # ========================================================

        {
            "category": "Pizza & Pasta",
            "name": "Four Cheese Pizza",
            "image": "four_cheese_pizza.jpg",
            "description": (
                "Handcrafted pizza topped with a rich blend of four "
                "Italian-style cheeses."
            ),
            "price": Decimal("480.00"),
        },
        {
            "category": "Pizza & Pasta",
            "name": "Margherita Pizza",
            "image": "margherita_pizza.jpg",
            "description": (
                "Classic pizza topped with tomato sauce, mozzarella and "
                "fresh basil."
            ),
            "price": Decimal("350.00"),
        },
        {
            "category": "Pizza & Pasta",
            "name": "Lobster Ravioli",
            "image": "lobster_ravioli.jpg",
            "description": (
                "Delicate ravioli filled with lobster and served with a "
                "refined creamy sauce."
            ),
            "price": Decimal("620.00"),
        },
        {
            "category": "Pizza & Pasta",
            "name": "Penne Arrabbiata",
            "image": "penne_arrabbiata.jpg",
            "description": (
                "Penne pasta tossed in a spicy tomato, garlic and herb "
                "sauce."
            ),
            "price": Decimal("330.00"),
        },
        {
            "category": "Pizza & Pasta",
            "name": "Truffle Tagliatelle",
            "image": "truffle_tagliatelle.jpg",
            "description": (
                "Fresh tagliatelle finished with parmesan and aromatic "
                "black truffle."
            ),
            "price": Decimal("520.00"),
        },
        {
            "category": "Pizza & Pasta",
            "name": "Wild Mushroom Risotto",
            "image": "wild_mushroom_risotto.jpg",
            "description": (
                "Creamy Italian risotto prepared with wild mushrooms, "
                "parmesan and herbs."
            ),
            "price": Decimal("440.00"),
        },

        # ========================================================
        # ASIAN & JAPANESE
        # ========================================================

        {
            "category": "Asian & Japanese",
            "name": "Salmon Sushi Platter",
            "image": "salmon_sushi_platter.jpg",
            "description": (
                "A selection of fresh salmon sushi prepared with seasoned "
                "Japanese rice."
            ),
            "price": Decimal("580.00"),
        },
        {
            "category": "Asian & Japanese",
            "name": "Vegetable Sushi Rolls",
            "image": "vegetable_sushi_rolls.jpg",
            "description": (
                "Fresh vegetable sushi rolls prepared with seasoned "
                "Japanese rice."
            ),
            "price": Decimal("360.00"),
        },
        {
            "category": "Asian & Japanese",
            "name": "Pad Thai with Prawns",
            "image": "pad_thai_with_prawns.jpg",
            "description": (
                "Thai rice noodles stir-fried with prawns, vegetables, "
                "peanuts and a traditional sauce."
            ),
            "price": Decimal("450.00"),
        },

        # ========================================================
        # DESSERTS
        # ========================================================

        {
            "category": "Desserts",
            "name": "Chocolate Fondant",
            "image": "chocolate_fondant.jpg",
            "description": (
                "Warm chocolate dessert with a rich molten centre."
            ),
            "price": Decimal("320.00"),
        },
        {
            "category": "Desserts",
            "name": "Classic Crème Brûlée",
            "image": "classic_crème_brûlée.jpg",
            "description": (
                "Silky vanilla custard finished with a crisp caramelised "
                "sugar crust."
            ),
            "price": Decimal("300.00"),
        },
        {
            "category": "Desserts",
            "name": "Japanese Matcha Cheesecake",
            "image": "japanese_matcha_cheesecake.jpg",
            "description": (
                "Creamy Japanese-style cheesecake infused with delicate "
                "matcha flavour."
            ),
            "price": Decimal("340.00"),
        },
        {
            "category": "Desserts",
            "name": "Mango & Passion Fruit Panna Cotta",
            "image": "mango_&_passion_fruit_panna_cotta.jpg",
            "description": (
                "Silky Italian panna cotta served with tropical mango "
                "and passion fruit."
            ),
            "price": Decimal("320.00"),
        },
        {
            "category": "Desserts",
            "name": "New York Cheesecake",
            "image": "new_york_cheesecake.jpg",
            "description": (
                "Classic rich and creamy cheesecake with a buttery biscuit "
                "base."
            ),
            "price": Decimal("320.00"),
        },
        {
            "category": "Desserts",
            "name": "Tiramisu",
            "image": "tiramisu.jpg",
            "description": (
                "Classic Italian dessert layered with coffee-soaked "
                "ladyfingers, mascarpone and cocoa."
            ),
            "price": Decimal("320.00"),
        },

        # ========================================================
        # COFFEE & BEVERAGES
        # ========================================================

        {
            "category": "Coffee & Beverages",
            "name": "Classic Cappuccino",
            "image": "classic_cappuccino.jpg",
            "description": (
                "Espresso with silky steamed milk and a light foam finish."
            ),
            "price": Decimal("180.00"),
        },
        {
            "category": "Coffee & Beverages",
            "name": "Fresh Mango & Passion Fruit Cooler",
            "image": "fresh_mango_&_passion_fruit_cooler.jpg",
            "description": (
                "Refreshing tropical cooler made with mango and passion "
                "fruit."
            ),
            "price": Decimal("240.00"),
        },
        {
            "category": "Coffee & Beverages",
            "name": "Moroccan Mint Tea",
            "image": "moroccan_mint_tea.jpg",
            "description": (
                "Refreshing green tea infused with fresh mint and served "
                "in Moroccan style."
            ),
            "price": Decimal("180.00"),
        },
        {
            "category": "Coffee & Beverages",
            "name": "Thai Iced Tea",
            "image": "thai_iced_tea.jpg",
            "description": (
                "Chilled Thai tea blended with milk and served over ice."
            ),
            "price": Decimal("190.00"),
        },
    ]

    def handle(self, *args, **options):
        created_tables = 0
        created_categories = 0
        created_items = 0
        updated_items = 0
        missing_images = []

        # ========================================================
        # TABLES
        # ========================================================

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

        # ========================================================
        # CATEGORIES
        # ========================================================

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

        # ========================================================
        # MENU ITEMS
        # ========================================================

        valid_item_names = {
            item_data["name"] for item_data in self.MENU_ITEMS
        }

        # Hide old demo menu items so the new international menu
        # becomes the active menu without deleting records that may
        # already be referenced by orders.
        MenuItem.objects.exclude(
            name__in=valid_item_names
        ).filter(
            is_available=True
        ).update(
            is_available=False
        )

        media_menu_dir = Path(settings.MEDIA_ROOT) / "menu"

        for item_data in self.MENU_ITEMS:
            category = categories[item_data["category"]]

            image_relative_path = f"menu/{item_data['image']}"
            image_absolute_path = media_menu_dir / item_data["image"]

            if not image_absolute_path.exists():
                missing_images.append(item_data["image"])

            item, created = MenuItem.objects.get_or_create(
                category=category,
                name=item_data["name"],
                defaults={
                    "description": item_data["description"],
                    "price": item_data["price"],
                    "is_available": True,
                    "image": image_relative_path,
                },
            )

            if created:
                created_items += 1
                continue

            changed = False

            if item.category_id != category.id:
                item.category = category
                changed = True

            if item.description != item_data["description"]:
                item.description = item_data["description"]
                changed = True

            if item.price != item_data["price"]:
                item.price = item_data["price"]
                changed = True

            if not item.is_available:
                item.is_available = True
                changed = True

            current_image = str(item.image) if item.image else ""

            if current_image != image_relative_path:
                item.image = image_relative_path
                changed = True

            if changed:
                item.save()
                updated_items += 1

        # ========================================================
        # OUTPUT
        # ========================================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "IDDS international restaurant menu is ready."
            )
        )
        self.stdout.write("")

        self.stdout.write(
            f"Tables created: {created_tables}"
        )

        self.stdout.write(
            f"Categories created: {created_categories}"
        )

        self.stdout.write(
            f"Menu items created: {created_items}"
        )

        self.stdout.write(
            f"Menu items updated: {updated_items}"
        )

        self.stdout.write(
            f"Images expected: {len(self.MENU_ITEMS)}"
        )

        self.stdout.write(
            f"Missing images: {len(missing_images)}"
        )

        if missing_images:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "The following image files were not found in media/menu:"
                )
            )

            for image_name in missing_images:
                self.stdout.write(f"  - {image_name}")