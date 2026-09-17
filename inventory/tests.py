from decimal import Decimal

from django.test import TestCase

from .models import Ingredient, StockMovement


class InventoryTests(TestCase):

    def setUp(self):
        self.ingredient = Ingredient.objects.create(
            name="Test Flour",
            unit="kg",
            current_stock=Decimal("10.00"),
            minimum_stock=Decimal("2.00"),
            reorder_level=Decimal("5.00"),
            cost_per_unit=Decimal("50.00"),
            supplier_name="Test Supplier",
            is_active=True,
        )

    def test_ingredient_is_created(self):
        self.assertEqual(
            self.ingredient.name,
            "Test Flour",
        )

    def test_low_stock_detection(self):
        self.ingredient.current_stock = Decimal("2.00")
        self.ingredient.save()

        self.assertTrue(
            self.ingredient.is_low_stock
        )

    def test_normal_stock_detection(self):
        self.ingredient.current_stock = Decimal("10.00")
        self.ingredient.save()

        self.assertFalse(
            self.ingredient.is_low_stock
        )

    def test_stock_movement_total_cost(self):
        movement = StockMovement.objects.create(
            ingredient=self.ingredient,
            movement_type="purchase",
            quantity=Decimal("5.00"),
            unit_cost=Decimal("50.00"),
            reference="TEST-001",
            notes="Test purchase",
        )

        self.assertEqual(
            movement.total_cost,
            Decimal("250.00"),
        )