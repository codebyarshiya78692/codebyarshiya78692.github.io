from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import DiningSession, Order
from restaurant.models import DiningTable


User = get_user_model()


class KitchenTests(TestCase):

    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff",
            password="StaffPassword123",
            is_staff=True,
        )

        self.customer = User.objects.create_user(
            username="customer",
            password="CustomerPassword123",
        )

        self.table = DiningTable.objects.create(
            table_number=10,
            capacity=4,
            status="occupied",
        )

        self.session = DiningSession.objects.create(
            table=self.table,
            customer_name="Test Customer",
            status="active",
        )

        self.order = Order.objects.create(
            session=self.session,
            status="new",
        )

    def test_kitchen_requires_staff(self):
        self.client.login(
            username="customer",
            password="CustomerPassword123",
        )

        response = self.client.get(
            reverse("kitchen:dashboard")
        )

        self.assertNotEqual(
            response.status_code,
            200,
        )

    def test_staff_can_open_kitchen(self):
        self.client.login(
            username="staff",
            password="StaffPassword123",
        )

        response = self.client.get(
            reverse("kitchen:dashboard")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_staff_can_accept_order(self):
        self.client.login(
            username="staff",
            password="StaffPassword123",
        )

        response = self.client.post(
            reverse(
                "kitchen:accept_order",
                args=[self.order.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "accepted",
        )