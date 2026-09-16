from django.db import models


class DiningTable(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("order_in_progress", "Order in Progress"),
        ("billing", "Billing"),
        ("completed", "Completed"),
    ]

    table_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(default=2)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="available",
    )

    def __str__(self):
        return f"Table {self.table_number}"


class MenuCategory(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    description = models.TextField(
        blank=True,
    )

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.CASCADE,
        related_name="items",
    )

    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    is_available = models.BooleanField(
        default=True,
    )

    # Actual food image uploaded through Django Admin
    image = models.ImageField(
        upload_to="menu/",
        blank=True,
        null=True,
        help_text="Upload the food image for this menu item.",
    )

    def __str__(self):
        return self.name