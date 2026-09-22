import uuid

from django.conf import settings
from django.db import models

from restaurant.models import DiningTable, MenuItem


class DiningSession(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    table = models.ForeignKey(
        DiningTable,
        on_delete=models.PROTECT,
        related_name="dining_sessions",
    )

    session_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    customer_name = models.CharField(
        max_length=100,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        customer = self.customer_name or "Guest"
        return f"{customer} - Table {self.table.table_number}"

    @property
    def total_amount(self):
        return sum(
            order.total_amount
            for order in self.orders.all()
        )


class Order(models.Model):

    STATUS_CHOICES = [
        ("new", "New"),
        ("accepted", "Accepted"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("served", "Served"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    session = models.ForeignKey(
        DiningSession,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    # ---------------------------------------------------------
    # CHEF ASSIGNMENT
    # ---------------------------------------------------------
    #
    # All chefs can see a NEW order.
    # Once one chef accepts it, the order is assigned to
    # that chef and disappears from the other chefs' work queue.
    #
    assigned_chef = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
        limit_choices_to={
            "groups__name": "Chef",
        },
    )

    special_instructions = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    preparing_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    ready_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    served_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"Order #{self.id} - "
            f"Table {self.session.table.table_number}"
        )

    @property
    def total_amount(self):
        return sum(
            item.total_price
            for item in self.items.all()
        )


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name="order_items",
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

    special_instructions = models.CharField(
        max_length=255,
        blank=True,
    )

    def save(self, *args, **kwargs):

        if not self.item_name:
            self.item_name = self.menu_item.name

        if self.unit_price is None:
            self.unit_price = self.menu_item.price

        super().save(
            *args,
            **kwargs,
        )

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return (
            f"{self.item_name} x {self.quantity}"
        )


class ServiceRequest(models.Model):

    REQUEST_TYPES = [
        ("water", "Water"),
        ("cutlery", "Cutlery"),
        ("tissue", "Tissues"),
        ("assistance", "Assistance"),
        ("bill", "Bill"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("accepted", "Accepted"),
        ("completed", "Completed"),
    ]

    session = models.ForeignKey(
        DiningSession,
        on_delete=models.CASCADE,
        related_name="service_requests",
    )

    request_type = models.CharField(
        max_length=30,
        choices=REQUEST_TYPES,
    )

    message = models.CharField(
        max_length=255,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="requested",
    )

    # ---------------------------------------------------------
    # WAITER ASSIGNMENT
    # ---------------------------------------------------------

    assigned_waiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_service_requests",
        limit_choices_to={
            "groups__name": "Waiter",
        },
    )

    requested_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.get_request_type_display()} - "
            f"Table {self.session.table.table_number}"
        )