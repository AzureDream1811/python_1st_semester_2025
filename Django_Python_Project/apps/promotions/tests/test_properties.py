"""
Property-Based Tests for Promotion System
Using Hypothesis to test correctness properties
"""
import pytest
from decimal import Decimal
from datetime import timedelta
from hypothesis import given, strategies as st, settings
from django.test import TestCase
from django.utils import timezone

from apps.promotions.models import Voucher, ComboDeal
from apps.promotions.services import PromotionService


class TestVoucherValidation(TestCase):
    """
    **Feature: advanced-features, Property 8: Voucher validation chính xác**
    **Validates: Requirements 3.2**
    """

    def setUp(self):
        self.service = PromotionService()

    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=100)
    def test_expired_voucher_invalid(self, days_expired):
        """Property 8: Expired vouchers must return invalid"""
        # Create expired voucher
        voucher = Voucher.objects.create(
            code=f'EXPIRED{days_expired}',
            name='Expired Voucher',
            discount_type='percentage',
            discount_value=10,
            valid_from=timezone.now() - timedelta(days=days_expired + 10),
            valid_until=timezone.now() - timedelta(days=days_expired),
            is_active=True
        )

        result = self.service.validate_voucher(voucher.code, Decimal('100000'))

        self.assertFalse(result['valid'])
        self.assertIn('hết hạn', result['error'].lower())

        voucher.delete()

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100)
    def test_used_up_voucher_invalid(self, usage_limit):
        """Property 8: Vouchers with used_count >= usage_limit must be invalid"""
        voucher = Voucher.objects.create(
            code=f'USEDUP{usage_limit}',
            name='Used Up Voucher',
            discount_type='fixed',
            discount_value=50000,
            usage_limit=usage_limit,
            used_count=usage_limit,  # Already used up
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True
        )

        result = self.service.validate_voucher(voucher.code, Decimal('100000'))

        self.assertFalse(result['valid'])
        self.assertIn('hết lượt', result['error'].lower())

        voucher.delete()


class TestVoucherDiscount(TestCase):
    """
    **Feature: advanced-features, Property 9: Áp dụng voucher tính đúng số tiền giảm**
    **Validates: Requirements 3.1**
    """

    def setUp(self):
        self.service = PromotionService()

    @given(
        st.integers(min_value=100000, max_value=10000000),
        st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=100)
    def test_percentage_discount_calculation(self, cart_total, discount_percent):
        """Property 9: Percentage discount = cart_total * percent / 100"""
        voucher = Voucher.objects.create(
            code=f'PERCENT{discount_percent}',
            name='Percentage Voucher',
            discount_type='percentage',
            discount_value=discount_percent,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True
        )

        cart = Decimal(str(cart_total))
        expected_discount = cart * Decimal(str(discount_percent)) / 100

        actual_discount = self.service.calculate_discount(voucher, cart)

        self.assertEqual(actual_discount, expected_discount)

        voucher.delete()

    @given(
        st.integers(min_value=100000, max_value=10000000),
        st.integers(min_value=10000, max_value=500000)
    )
    @settings(max_examples=100)
    def test_fixed_discount_calculation(self, cart_total, discount_value):
        """Property 9: Fixed discount = discount_value (capped at cart_total)"""
        voucher = Voucher.objects.create(
            code=f'FIXED{discount_value}',
            name='Fixed Voucher',
            discount_type='fixed',
            discount_value=discount_value,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True
        )

        cart = Decimal(str(cart_total))
        expected_discount = min(Decimal(str(discount_value)), cart)

        actual_discount = self.service.calculate_discount(voucher, cart)

        self.assertEqual(actual_discount, expected_discount)

        voucher.delete()


class TestComboDeal(TestCase):
    """
    **Feature: advanced-features, Property 10: Combo deal tự động áp dụng**
    **Validates: Requirements 3.4**
    """

    def setUp(self):
        self.service = PromotionService()
        from apps.products.models import Product, Category

        self.category = Category.objects.create(name='Test Category Combo', is_active=True)
        self.product1 = Product.objects.create(
            name='Combo Product 1',
            description='Test',
            category=self.category,
            price=Decimal('1000000'),
            stock=10,
            is_active=True,
            image='products/test.jpg'
        )
        self.product2 = Product.objects.create(
            name='Combo Product 2',
            description='Test',
            category=self.category,
            price=Decimal('500000'),
            stock=10,
            is_active=True,
            image='products/test.jpg'
        )

    def test_combo_detected_when_all_products_in_cart(self):
        """Property 10: Combo must be detected when cart contains all combo products"""
        # Create combo deal
        combo = ComboDeal.objects.create(
            name='Test Combo',
            discount_type='percentage',
            discount_value=10,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True
        )
        combo.products.add(self.product1, self.product2)

        # Cart with both products
        cart_items = [
            {'product_id': self.product1.id, 'quantity': 1},
            {'product_id': self.product2.id, 'quantity': 1}
        ]

        applicable_combos = self.service.check_combo_deals(cart_items)

        self.assertEqual(len(applicable_combos), 1)
        self.assertEqual(applicable_combos[0]['combo'].id, combo.id)

        combo.delete()

    def test_combo_not_detected_when_missing_products(self):
        """Property 10: Combo must NOT be detected when cart is missing products"""
        combo = ComboDeal.objects.create(
            name='Test Combo 2',
            discount_type='fixed',
            discount_value=100000,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True
        )
        combo.products.add(self.product1, self.product2)

        # Cart with only one product
        cart_items = [
            {'product_id': self.product1.id, 'quantity': 1}
        ]

        applicable_combos = self.service.check_combo_deals(cart_items)

        self.assertEqual(len(applicable_combos), 0)

        combo.delete()

    def tearDown(self):
        self.product1.delete()
        self.product2.delete()
        self.category.delete()
