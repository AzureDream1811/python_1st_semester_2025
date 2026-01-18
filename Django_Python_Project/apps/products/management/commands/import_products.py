"""
Management command để import dữ liệu sản phẩm từ file JSON
Sử dụng: python manage.py import_products --path=fixtures
"""
import json
import os
from django.core.management.base import BaseCommand
from apps.products.models import Category, Brand, Product


class Command(BaseCommand):
    help = 'Import products from JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default='fixtures',
            help='Path to JSON files directory'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import'
        )

    def handle(self, *args, **options):
        path = options['path']

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Product.objects.all().delete()
            Brand.objects.all().delete()
            Category.objects.all().delete()

        # Import Categories
        self.import_categories(os.path.join(path, 'categories.json'))

        # Import Brands
        self.import_brands(os.path.join(path, 'brands.json'))

        # Import Products from multiple files
        product_files = [
            'products.json',
            'products_laptops.json',
            'products_tablets.json',
            'products_accessories.json'
        ]

        for filename in product_files:
            filepath = os.path.join(path, filename)
            if os.path.exists(filepath):
                self.import_products(filepath)

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('IMPORT COMPLETED!'))
        self.stdout.write(f'Categories: {Category.objects.count()}')
        self.stdout.write(f'Brands: {Brand.objects.count()}')
        self.stdout.write(f'Products: {Product.objects.count()}')
        self.stdout.write(self.style.SUCCESS('=' * 50))

    def import_categories(self, filepath):
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
            return

        self.stdout.write(f'\nImporting categories from {filepath}...')

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        count = 0
        for item in data:
            category, created = Category.objects.update_or_create(
                name=item['name'],
                defaults={
                    'description': item.get('description', ''),
                    'is_active': item.get('is_active', True)
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {category.name}')
            count += 1

        self.stdout.write(self.style.SUCCESS(f'  Total categories: {count}'))

    def import_brands(self, filepath):
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
            return

        self.stdout.write(f'\nImporting brands from {filepath}...')

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        count = 0
        for item in data:
            brand, created = Brand.objects.update_or_create(
                name=item['name'],
                defaults={
                    'description': item.get('description', ''),
                    'is_active': item.get('is_active', True)
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {brand.name}')
            count += 1

        self.stdout.write(self.style.SUCCESS(f'  Total brands: {count}'))

    def import_products(self, filepath):
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
            return

        self.stdout.write(f'\nImporting products from {filepath}...')

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        count = 0
        for item in data:
            # Get category and brand
            category = Category.objects.filter(name=item['category']).first()
            brand = Brand.objects.filter(name=item.get('brand')).first() if item.get('brand') else None

            if not category:
                self.stdout.write(
                    self.style.WARNING(f'  Category not found: {item["category"]} - Skipping {item["name"]}'))
                continue

            product, created = Product.objects.update_or_create(
                name=item['name'],
                defaults={
                    'description': item['description'],
                    'category': category,
                    'brand': brand,
                    'price': item['price'],
                    'sale_price': item.get('sale_price'),
                    'stock': item.get('stock', 0),
                    'image': item.get('image', 'products/default.jpg'),
                    'specifications': item.get('specifications'),
                    'is_active': item.get('is_active', True),
                    'is_featured': item.get('is_featured', False),
                    'is_new': item.get('is_new', True)
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {product.name}')
            count += 1

        self.stdout.write(self.style.SUCCESS(f'  Total products from this file: {count}'))
