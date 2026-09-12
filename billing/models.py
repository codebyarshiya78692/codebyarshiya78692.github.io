from decimal import Decimal

from django.db import models

from orders.models import DiningSession, Order, OrderItem


class Bill(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("generated", "Generated"),
        ("completed", "Completed"),
    ]

    session = models.OneToOneField(
        DiningSession,
        on_delete=models.CASCADE,
        related_name="bill",
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    service_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )

    generated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Bill #{self.id} - Table {self.session.table.table_number}"


class BillItem(models.Model):
    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="items",
    )

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.PROTECT,
        related_name="bill_items",
    )

    item_name = models.CharField(
        max_length=150,
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"