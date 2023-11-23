from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import Order


class TestOrderManagers(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = [
            get_user_model().objects.create(username='TesterOne', password='strong_password')
        ]
        cls.orders = [
            Order.objects.create(user=cls.users[0]),  # not ordered, not done
            Order.objects.create(user=cls.users[0],
                                 ordered=True, ordered_at=timezone.now()),  # ordered, not done
            Order.objects.create(user=cls.users[0],
                                 ordered=True, ordered_at=timezone.now(),
                                 done=True, done_at=timezone.now())  # ordered, done
        ]

    def test_objects_manager_returns_all_objects(self):
        self.assertEqual(Order.objects.all().count(), len(self.orders))

    def test_baskets_manager_returns_not_ordered_and_not_done_orders(self):
        result = list(Order.baskets.all())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.orders[0])

    def test_active_orders_manager_returns_ordered_and_not_done_orders(self):
        result = list(Order.active_orders.all())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.orders[1])

    def test_finished_manager_returns_ordered_and_done_orders(self):
        result = list(Order.finished.all())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.orders[2])


class TestOrderMethods(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = [
            get_user_model().objects.create(username='TesterOne', password='strong_password'),
        ]

    def test_mark_ordered_on_order_changes_state(self):
        order = Order.objects.create(user=self.users[0], ship_to='Test location number one')
        order.mark_ordered()

        self.assertTrue(order.ordered)
        self.assertIsNotNone(order.ordered_at)

    def test_mark_ordered_doesnt_save(self):
        order = Order.objects.create(user=self.users[0], ship_to='Test location number one')
        order.mark_ordered()

        db_order = Order.objects.get(pk=order.pk)

        self.assertFalse(db_order.ordered)
        self.assertIsNone(db_order.ordered_at)

    def test_mark_ordered_without_ship_to_attribute_raises_BlankShipmentError(self):
        order = Order.objects.create(user=self.users[0])

        with self.assertRaises(Order.BlankShipmentError):
            order.mark_ordered()

    def test_mark_ordered_on_already_ordered_order_raises_WrongStateChange(self):
        order = Order.objects.create(user=self.users[0], ship_to='Test location number one')
        order.mark_ordered()

        with self.assertRaises(Order.WrongStateChange):
            order.mark_ordered()

    def test_mark_done_changes_state(self):
        order = Order.objects.create(user=self.users[0], ship_to='Test location number one')
        order.mark_ordered()

        order.mark_done()

        self.assertTrue(order.done)
        self.assertIsNotNone(order.done_at)

    def test_mark_done_doesnt_save(self):
        order = Order.objects.create(user=self.users[0], ship_to='Test location number one')
        order.mark_ordered()
        order.mark_done()

        db_order = Order.objects.get(pk=order.pk)

        self.assertFalse(db_order.done)
        self.assertIsNone(db_order.done_at)

    def test_mark_done_on_not_ordered_order_raises_WrongStateChange(self):
        order = Order.objects.create(user=self.users[0], ship_to='Test location number one')

        with self.assertRaises(Order.WrongStateChange):
            order.mark_done()

    def test_mark_done_on_already_done_order_raises_WrongStateChange(self):
        order = Order.objects.create(user=self.users[0], ship_to='Test location number one')
        order.mark_ordered()
        order.mark_done()

        with self.assertRaises(Order.WrongStateChange):
            order.mark_done()
