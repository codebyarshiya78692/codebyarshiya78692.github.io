from decimal import Decimal

from django.db import models


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("l", "Liter"),
        ("ml", "Milliliter"),
        ("pcs", "Pieces"),
        ("pack", "Pack"),
    ]

    name = models.CharField(
        max_length=150,
        unique=True,
    )

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default="pcs",
    )

    current_stock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal("0.000"),
    )

    minimum_stock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal("0.000"),
    )

    reorder_level = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal("0.000"),
    )

    cost_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    supplier_name = models.CharField(
        max_length=150,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ("purchase", "Purchase"),
        ("usage", "Usage"),
        ("adjustment", "Adjustment"),
        ("waste", "Waste"),
        ("return", "Return"),
    ]

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="movements",
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
    )

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    reference = models.CharField(
        max_length=150,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.ingredient.name} - "
            f"{self.movement_type} - "
            f"{self.quantity}"
        )

    @property
    def total_cost(self):
        return (
            self.quantity *
            self.unit_cost
        )