from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from restaurant.models import MenuItem


class Command(BaseCommand):
    help = "Attach existing menu images from media/menu to MenuItem records."

    IMAGE_MAP = {
        "Burrata with Heirloom Tomatoes": "burrata_with_heirloom_tomatoes.jpg",
        "Truffle Parmesan Arancini": "truffle_parmesan_arancini.jpg",
        "Chicken Satay with Peanut Sauce": "chickensataywithpeanutsauce.jpg",
        "Tuna Tartare with Avocado": "tuna_tartare_with_avocado.jpg",
        "Crispy Prawn Tempura": "crispy_prawn_tempura.jpg",
        "Chicken Tikka": "chicken_tikka.jpg",

        "French Onion Soup": "french_onion_soup.jpg",
        "Creamy Wild Mushroom Soup": "Creamy_Wild_Mushroom_Soup.jpg",
        "Classic Caesar Salad": "classic_caesar_salad.jpg",
        "Mediterranean Quinoa Salad": "mediterranean_quinoa_salad.jpg",
        "Thai Green Papaya Salad": "thai_green_papaya_salad.jpg",

        "Paneer Tikka": "paneer_tikka.jpg",
        "Butter Chicken": "butter_chicken.jpg",
        "Dal Makhani": "dal_makhani.jpg",
        "Hyderabadi Chicken Biryani": "hyderabadi_chicken_biryani.jpg",
        "Lamb Rogan Josh": "lamb_rogan_josh.jpg",

        "Wild Mushroom Risotto": "wild_mushroom_risotto.jpg",
        "Truffle Tagliatelle": "truffle_tagliatelle.jpg",
        "Lobster Ravioli": "lobster_ravioli.jpg",
        "Penne Arrabbiata": "penne_arrabbiata.jpg",
        "Margherita Pizza": "margherita_pizza.jpg",
        "Four Cheese Pizza": "four_cheese_pizza.jpg",

        "Chicken Tacos with Avocado Salsa": "chicken_tacos_with_avocado_salsa.jpg",
        "Beef Birria Tacos": "beef_birria_tacos.jpg",
        "Vegetable Quesadilla": "vegetable_quesadilla.jpg",
        "Chicken Enchiladas": "chicken_enchiladas.jpg",
        "Mexican Corn with Chipotle Mayo": "mexican_corn_with_chipotle_mayo.jpg",

        "Thai Green Curry": "thai_green_curry.jpg",
        "Thai Red Curry": "thai_red_curry.jpg",
        "Pad Thai with Prawns": "pad_thai_with_prawns.jpg",
        "Tom Yum Prawn Soup": "tom_yum_prawn_soup.jpg",
        "Thai Basil Chicken": "thai_basil_chicken.jpg",

        "Salmon Sushi Platter": "salmon_sushi_platter.jpg",
        "Vegetable Sushi Rolls": "vegetable_sushi_rolls.jpg",
        "Chicken Yakitori": "chicken_yakitori.jpg",
        "Miso Glazed Black Cod": "miso_glazed_black_cod.jpg",
        "Wagyu Beef Teriyaki": "wagyu_beef_teriyaki.jpg",

        "Classic Crème Brûlée": "classic_crème_brûlée.jpg",
        "Chocolate Fondant": "chocolate_fondant.jpg",
        "New York Cheesecake": "new_york_cheesecake.jpg",
        "Tiramisu": "tiramisu.jpg",
        "Mango & Passion Fruit Panna Cotta": "mango_&_passion_fruit_panna_cotta.jpg",
        "Japanese Matcha Cheesecake": "japanese_matcha_cheesecake.jpg",

        "Classic Cappuccino": "classic_cappuccino.jpg",
        "Moroccan Mint Tea": "moroccan_mint_tea.jpg",
        "Thai Iced Tea": "thai_iced_tea.jpg",
        "Fresh Mango & Passion Fruit Cooler": "fresh_mango_&_passion_fruit_cooler.jpg",
    }

    def handle(self, *args, **options):
        media_menu_dir = Path(settings.MEDIA_ROOT) / "menu"

        updated = 0
        already_correct = 0
        missing = 0
        database_missing = 0

        self.stdout.write("")
        self.stdout.write("Attaching menu images...")
        self.stdout.write("")

        for item_name, filename in self.IMAGE_MAP.items():

            item = MenuItem.objects.filter(
                name=item_name
            ).first()

            if item is None:
                database_missing += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"DATABASE ITEM NOT FOUND: {item_name}"
                    )
                )

                continue

            image_path = media_menu_dir / filename

            if not image_path.exists():
                missing += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"IMAGE FILE NOT FOUND: {filename}"
                    )
                )

                continue

            image_value = f"menu/{filename}"

            if item.image.name == image_value:
                already_correct += 1
                continue

            item.image = image_value
            item.save(update_fields=["image"])

            updated += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"ATTACHED: {item_name} -> {filename}"
                )
            )

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                "MENU IMAGE DATABASE UPDATE COMPLETE"
            )
        )
        self.stdout.write("=" * 60)

        self.stdout.write(
            f"Images attached: {updated}"
        )

        self.stdout.write(
            f"Already correct: {already_correct}"
        )

        self.stdout.write(
            f"Missing image files: {missing}"
        )

        self.stdout.write(
            f"Missing database items: {database_missing}"
        )

        self.stdout.write("")