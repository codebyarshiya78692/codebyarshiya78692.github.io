from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from restaurant.models import DiningTable, MenuCategory, MenuItem

from .models import DiningSession, Order, OrderItem


class OrdersTests(TestCase):

    def setUp(self):
        self.table = DiningTable.objects.create(
            table_number=999,
            capacity=4,
            status="available",
        )

        self.category = MenuCategory.objects.create(
            name="Test Category",
        )

        self.menu_item = MenuItem.objects.create(
            category=self.category,
            name="Test Burger",
            description="Test burger",
            price=250,
            is_available=True,
        )

    def _start_customer_session(self):
        dining_session = DiningSession.objects.create(
            table=self.table,
            customer_name="Test Customer",
            status="active",
        )

        session = self.client.session

        session["dining_session_id"] = dining_session.id
        session["table_id"] = self.table.id
        session["cart"] = {}

        session.save()

        return dining_session

    def test_cart_page_loads(self):
        self._start_customer_session()

        response = self.client.get(
            reverse("cart")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_add_item_to_cart(self):
        self._start_customer_session()

        response = self.client.post(
            reverse(
                "add_to_cart",
                args=[self.menu_item.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertTrue(
            data["success"]
        )

        cart = self.client.session.get(
            "cart",
            {},
        )

        self.assertIn(
            str(self.menu_item.id),
            cart,
        )

        self.assertEqual(
            cart[str(self.menu_item.id)],
            1,
        )

    def test_dining_session_can_be_created(self):
        session = DiningSession.objects.create(
            table=self.table,
            customer_name="Test Customer",
            status="active",
        )

        self.assertEqual(
            session.table,
            self.table,
        )

        self.assertEqual(
            session.status,
            "active",
        )

    def test_order_total(self):
        session = DiningSession.objects.create(
            table=self.table,
            customer_name="Test Customer",
            status="active",
        )

        order = Order.objects.create(
            session=session,
            status="new",
        )

        OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item,
            item_name=self.menu_item.name,
            unit_price=self.menu_item.price,
            quantity=2,
        )

        self.assertEqual(
            order.total_amount,
            Decimal("500"),
        )