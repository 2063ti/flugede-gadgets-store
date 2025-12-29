from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import (
    Category, Brand, Product, ProductImage, ProductSpecification,
    UserProfile, Cart, Coupon
)
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with sample data for FlugEde E-Commerce'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')
        
        # Create Categories
        self.stdout.write('Creating categories...')
        categories_data = [
            {'name': 'Smartphones', 'description': 'Latest smartphones from top brands'},
            {'name': 'Laptops', 'description': 'High-performance laptops for work and gaming'},
            {'name': 'Smart TVs', 'description': 'Smart TVs with stunning picture quality'},
            {'name': 'Headphones', 'description': 'Premium audio experience'},
            {'name': 'Smartwatches', 'description': 'Stay connected on the go'},
            {'name': 'Tablets', 'description': 'Portable computing devices'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(f'  Created category: {cat.name}')
        
        # Create Brands
        self.stdout.write('Creating brands...')
        brands_data = [
            'Apple', 'Samsung', 'OnePlus', 'Xiaomi', 'Realme',
            'Dell', 'HP', 'Lenovo', 'ASUS', 'Sony',
            'LG', 'Boat', 'JBL', 'Noise', 'Fitbit'
        ]
        
        brands = {}
        for brand_name in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={
                    'slug': slugify(brand_name),
                    'is_active': True
                }
            )
            brands[brand_name] = brand
            if created:
                self.stdout.write(f'  Created brand: {brand.name}')
        
        # Create Products
        self.stdout.write('Creating products...')
        products_data = [
            # Smartphones
            {
                'name': 'iPhone 15 Pro Max',
                'category': 'Smartphones',
                'brand': 'Apple',
                'description': 'The most powerful iPhone ever with A17 Pro chip, titanium design, and advanced camera system.',
                'price': Decimal('134900'),
                'discount_price': Decimal('129900'),
                'stock': 50,
                'is_featured': True,
                'warranty_period': '1 Year',
                'specs': [
                    {'name': 'Display', 'value': '6.7" Super Retina XDR'},
                    {'name': 'Processor', 'value': 'A17 Pro'},
                    {'name': 'RAM', 'value': '8GB'},
                    {'name': 'Storage', 'value': '256GB'},
                    {'name': 'Camera', 'value': '48MP + 12MP + 12MP'},
                    {'name': 'Battery', 'value': '4422mAh'},
                ]
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'category': 'Smartphones',
                'brand': 'Samsung',
                'description': 'Premium flagship with S Pen, 200MP camera, and AI-powered features.',
                'price': Decimal('129999'),
                'discount_price': Decimal('119999'),
                'stock': 45,
                'is_featured': True,
                'warranty_period': '1 Year',
                'specs': [
                    {'name': 'Display', 'value': '6.8" Dynamic AMOLED 2X'},
                    {'name': 'Processor', 'value': 'Snapdragon 8 Gen 3'},
                    {'name': 'RAM', 'value': '12GB'},
                    {'name': 'Storage', 'value': '256GB'},
                    {'name': 'Camera', 'value': '200MP + 50MP + 12MP + 10MP'},
                    {'name': 'Battery', 'value': '5000mAh'},
                ]
            },
            {
                'name': 'OnePlus 12',
                'category': 'Smartphones',
                'brand': 'OnePlus',
                'description': 'Flagship killer with Hasselblad camera and 100W fast charging.',
                'price': Decimal('64999'),
                'discount_price': Decimal('59999'),
                'stock': 60,
                'is_featured': True,
                'warranty_period': '1 Year',
                'specs': [
                    {'name': 'Display', 'value': '6.82" AMOLED'},
                    {'name': 'Processor', 'value': 'Snapdragon 8 Gen 3'},
                    {'name': 'RAM', 'value': '12GB'},
                    {'name': 'Storage', 'value': '256GB'},
                    {'name': 'Camera', 'value': '50MP + 64MP + 48MP'},
                    {'name': 'Battery', 'value': '5400mAh'},
                ]
            },
            # Laptops
            {
                'name': 'MacBook Pro 16" M3 Pro',
                'category': 'Laptops',
                'brand': 'Apple',
                'description': 'Professional laptop with M3 Pro chip, stunning Liquid Retina XDR display.',
                'price': Decimal('249900'),
                'discount_price': Decimal('239900'),
                'stock': 25,
                'is_featured': True,
                'warranty_period': '1 Year',
                'specs': [
                    {'name': 'Display', 'value': '16.2" Liquid Retina XDR'},
                    {'name': 'Processor', 'value': 'Apple M3 Pro'},
                    {'name': 'RAM', 'value': '18GB Unified Memory'},
                    {'name': 'Storage', 'value': '512GB SSD'},
                    {'name': 'Graphics', 'value': 'Integrated GPU'},
                    {'name': 'Battery', 'value': 'Up to 22 hours'},
                ]
            },
            {
                'name': 'Dell XPS 15',
                'category': 'Laptops',
                'brand': 'Dell',
                'description': 'Premium Windows laptop with InfinityEdge display and powerful performance.',
                'price': Decimal('159999'),
                'discount_price': Decimal('149999'),
                'stock': 30,
                'is_featured': False,
                'warranty_period': '1 Year',
                'specs': [
                    {'name': 'Display', 'value': '15.6" FHD+ InfinityEdge'},
                    {'name': 'Processor', 'value': 'Intel Core i7-13700H'},
                    {'name': 'RAM', 'value': '16GB DDR5'},
                    {'name': 'Storage', 'value': '512GB SSD'},
                    {'name': 'Graphics', 'value': 'NVIDIA RTX 4050'},
                    {'name': 'Battery', 'value': 'Up to 10 hours'},
                ]
            },
            # Smart TVs
            {
                'name': 'Samsung 65" Neo QLED 4K',
                'category': 'Smart TVs',
                'brand': 'Samsung',
                'description': 'Quantum HDR with Neural Quantum Processor for stunning picture quality.',
                'price': Decimal('189999'),
                'discount_price': Decimal('169999'),
                'stock': 15,
                'is_featured': True,
                'warranty_period': '2 Years',
                'specs': [
                    {'name': 'Screen Size', 'value': '65 inches'},
                    {'name': 'Resolution', 'value': '4K UHD (3840x2160)'},
                    {'name': 'Display Type', 'value': 'Neo QLED'},
                    {'name': 'HDR', 'value': 'Quantum HDR 32X'},
                    {'name': 'Smart TV', 'value': 'Tizen OS'},
                    {'name': 'Refresh Rate', 'value': '120Hz'},
                ]
            },
            {
                'name': 'LG 55" OLED evo C3',
                'category': 'Smart TVs',
                'brand': 'LG',
                'description': 'Self-lit OLED pixels for perfect blacks and infinite contrast.',
                'price': Decimal('149999'),
                'discount_price': Decimal('139999'),
                'stock': 20,
                'is_featured': True,
                'warranty_period': '2 Years',
                'specs': [
                    {'name': 'Screen Size', 'value': '55 inches'},
                    {'name': 'Resolution', 'value': '4K UHD (3840x2160)'},
                    {'name': 'Display Type', 'value': 'OLED evo'},
                    {'name': 'HDR', 'value': 'Dolby Vision IQ'},
                    {'name': 'Smart TV', 'value': 'webOS'},
                    {'name': 'Refresh Rate', 'value': '120Hz'},
                ]
            },
            # Headphones
            {
                'name': 'Sony WH-1000XM5',
                'category': 'Headphones',
                'brand': 'Sony',
                'description': 'Industry-leading noise cancellation with premium sound quality.',
                'price': Decimal('29990'),
                'discount_price': Decimal('26990'),
                'stock': 75,
                'is_featured': False,
                'warranty_period': '1 Year',
                'specs': [
                    {'name': 'Type', 'value': 'Over-Ear Wireless'},
                    {'name': 'Noise Cancellation', 'value': 'Active (ANC)'},
                    {'name': 'Battery Life', 'value': 'Up to 30 hours'},
                    {'name': 'Connectivity', 'value': 'Bluetooth 5.2'},
                    {'name': 'Driver Size', 'value': '30mm'},
                ]
            },
        ]
        
        for prod_data in products_data:
            specs = prod_data.pop('specs', [])
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'slug': slugify(prod_data['name']),
                    'category': categories[prod_data['category']],
                    'brand': brands[prod_data['brand']],
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'discount_price': prod_data.get('discount_price'),
                    'stock': prod_data['stock'],
                    'is_featured': prod_data.get('is_featured', False),
                    'warranty_period': prod_data.get('warranty_period', ''),
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'  Created product: {product.name}')
                
                # Add specifications
                for idx, spec in enumerate(specs):
                    ProductSpecification.objects.create(
                        product=product,
                        name=spec['name'],
                        value=spec['value'],
                        order=idx
                    )
        
        # Create Coupons
        self.stdout.write('Creating coupons...')
        coupons_data = [
            {
                'code': 'WELCOME10',
                'discount_type': 'percentage',
                'discount_value': Decimal('10'),
                'min_purchase_amount': Decimal('5000'),
                'max_discount_amount': Decimal('1000'),
            },
            {
                'code': 'FLAT500',
                'discount_type': 'fixed',
                'discount_value': Decimal('500'),
                'min_purchase_amount': Decimal('10000'),
                'max_discount_amount': None,
            },
            {
                'code': 'MEGA20',
                'discount_type': 'percentage',
                'discount_value': Decimal('20'),
                'min_purchase_amount': Decimal('20000'),
                'max_discount_amount': Decimal('5000'),
            },
        ]
        
        for coupon_data in coupons_data:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults={
                    'discount_type': coupon_data['discount_type'],
                    'discount_value': coupon_data['discount_value'],
                    'min_purchase_amount': coupon_data['min_purchase_amount'],
                    'max_discount_amount': coupon_data['max_discount_amount'],
                    'valid_from': timezone.now(),
                    'valid_to': timezone.now() + timedelta(days=30),
                    'usage_limit': 100,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created coupon: {coupon.code}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data!'))
        self.stdout.write(self.style.SUCCESS('You can now create a superuser with: python manage.py createsuperuser'))
