from decimal import Decimal

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from orders.models import DiningSession
from orders.models import Order
from orders.models import OrderItem

from restaurant.models import DiningTable
from restaurant.models import MenuCategory
from restaurant.models import MenuItem

from .models import Bill


class BillingWorkflowTests(TestCase):

    def setUp(self):

        waiter_group = Group.objects.create(
            name="Waiter"
        )

        self.waiter = User.objects.create_user(
            username="waiter",
            password="Waiter@12345",
        )

        self.waiter.groups.add(
            waiter_group
        )

        category = MenuCategory.objects.create(
            name="Test Food"
        )

        item = MenuItem.objects.create(
            category=category,
            name="Test Dish",
            description="Test dish",
            price=Decimal("200.00"),
            is_available=True,
        )

        self.table = DiningTable.objects.create(
            table_number=501,
            capacity=2,
            status="occupied",
        )

        self.session = DiningSession.objects.create(
            table=self.table,
            customer_name="Test Guest",
            status="active",
        )

        self.order = Order.objects.create(
            session=self.session,
            status="served",
        )

        OrderItem.objects.create(
            order=self.order,
            menu_item=item,
            item_name=item.name,
            unit_price=item.price,
            quantity=2,
        )

        self.client.login(
            username="waiter",
            password="Waiter@12345",
        )


    def test_generate_bill_is_post_only_and_calculates_totals(self):

        response = self.client.post(
            reverse(
                "billing:generate_bill",
                args=[self.session.id],
            )
        )

        bill = Bill.objects.get(
            session=self.session
        )

        self.assertRedirects(
            response,
            reverse(
                "billing:bill_detail",
                args=[bill.id],
            ),
            fetch_redirect_response=False,
        )

        self.assertEqual(
            bill.status,
            "generated",
        )

        self.assertEqual(
            bill.subtotal,
            Decimal("400.00"),
        )

        self.assertEqual(
            bill.tax,
            Decimal("20.00"),
        )

        self.assertEqual(
            bill.service_charge,
            Decimal("40.00"),
        )

        self.assertEqual(
            bill.total_amount,
            Decimal("460.00"),
        )

        self.table.refresh_from_db()

        self.assertEqual(
            self.table.status,
            "billing",
        )


    def test_complete_bill_records_payment_and_releases_table(self):

        self.client.post(
            reverse(
                "billing:generate_bill",
                args=[self.session.id],
            )
        )

        bill = Bill.objects.get(
            session=self.session
        )

        response = self.client.post(
            reverse(
                "billing:complete_bill",
                args=[bill.id],
            ),
            {
                "payment_method": "upi",
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "billing:bill_detail",
                args=[bill.id],
            ),
            fetch_redirect_response=False,
        )

        bill.refresh_from_db()
        self.session.refresh_from_db()
        self.table.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(
            bill.status,
            "completed",
        )

        self.assertEqual(
            bill.payment_method,
            "upi",
        )

        self.assertIsNotNone(
            bill.paid_at
        )

        self.assertEqual(
            self.session.status,
            "completed",
        )

        self.assertEqual(
            self.order.status,
            "completed",
        )

        self.assertEqual(
            self.table.status,
            "available",
        )


    def test_invalid_payment_method_does_not_close_session(self):

        self.client.post(
            reverse(
                "billing:generate_bill",
                args=[self.session.id],
            )
        )

        bill = Bill.objects.get(
            session=self.session
        )

        response = self.client.post(
            reverse(
                "billing:complete_bill",
                args=[bill.id],
            ),
            {
                "payment_method": "bitcoin",
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "billing:bill_detail",
                args=[bill.id],
            ),
            fetch_redirect_response=False,
        )

        bill.refresh_from_db()
        self.session.refresh_from_db()
        self.table.refresh_from_db()

        self.assertEqual(
            bill.status,
            "generated",
        )

        self.assertEqual(
            self.session.status,
            "active",
        )

        self.assertEqual(
            self.table.status,
            "billing",
        )