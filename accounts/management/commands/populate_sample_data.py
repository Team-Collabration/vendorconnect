from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import User, VendorProfile, SupplierProfile
from products.models import Category, Product, SupplierProduct
from reviews.models import Review, ProductReview
from orders.models import Order, OrderItem, OrderStatusHistory
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data for VendorConnect'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {'name': 'Vegetables', 'description': 'Fresh vegetables', 'icon': 'fas fa-carrot'},
            {'name': 'Fruits', 'description': 'Fresh fruits', 'icon': 'fas fa-apple-alt'},
            {'name': 'Grains', 'description': 'Rice, wheat, pulses', 'icon': 'fas fa-seedling'},
            {'name': 'Dairy', 'description': 'Milk, cheese, butter', 'icon': 'fas fa-cheese'},
            {'name': 'Spices', 'description': 'Whole and ground spices', 'icon': 'fas fa-pepper-hot'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create products
        products_data = [
            {'name': 'Tomatoes', 'category': categories[0], 'unit': 'kg', 'description': 'Fresh red tomatoes'},
            {'name': 'Onions', 'category': categories[0], 'unit': 'kg', 'description': 'Fresh onions'},
            {'name': 'Potatoes', 'category': categories[0], 'unit': 'kg', 'description': 'Fresh potatoes'},
            {'name': 'Bananas', 'category': categories[1], 'unit': 'dozen', 'description': 'Yellow bananas'},
            {'name': 'Apples', 'category': categories[1], 'unit': 'kg', 'description': 'Red apples'},
            {'name': 'Rice', 'category': categories[2], 'unit': 'kg', 'description': 'Basmati rice'},
            {'name': 'Wheat Flour', 'category': categories[2], 'unit': 'kg', 'description': 'Whole wheat flour'},
            {'name': 'Milk', 'category': categories[3], 'unit': 'l', 'description': 'Fresh cow milk'},
            {'name': 'Paneer', 'category': categories[3], 'unit': 'kg', 'description': 'Fresh paneer'},
            {'name': 'Black Pepper', 'category': categories[4], 'unit': 'kg', 'description': 'Whole black pepper'},
        ]
        
        products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults=prod_data
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create sample users and profiles
        users_data = [
            # Vendors
            {
                'username': 'vendor1', 'email': 'vendor1@example.com', 'password': 'testpass123',
                'user_type': 'vendor', 'phone_number': '+919876543210',
                'business_name': 'Street Food Corner', 'business_type': 'Street Food',
                'address': '123 Main Street', 'city': 'Mumbai', 'state': 'Maharashtra', 'pincode': '400001'
            },
            {
                'username': 'vendor2', 'email': 'vendor2@example.com', 'password': 'testpass123',
                'user_type': 'vendor', 'phone_number': '+919876543211',
                'business_name': 'Quick Bites', 'business_type': 'Fast Food',
                'address': '456 Park Avenue', 'city': 'Delhi', 'state': 'Delhi', 'pincode': '110001'
            },
            # Suppliers
            {
                'username': 'supplier1', 'email': 'supplier1@example.com', 'password': 'testpass123',
                'user_type': 'supplier', 'phone_number': '+919876543212',
                'business_name': 'Fresh Farm Supplies', 'business_type': 'Wholesale',
                'address': '789 Farm Road', 'city': 'Mumbai', 'state': 'Maharashtra', 'pincode': '400002',
                'delivery_radius': 30, 'minimum_order_amount': 500, 'delivery_charge': 50
            },
            {
                'username': 'supplier2', 'email': 'supplier2@example.com', 'password': 'testpass123',
                'user_type': 'supplier', 'phone_number': '+919876543213',
                'business_name': 'Quality Groceries', 'business_type': 'Retail',
                'address': '321 Market Street', 'city': 'Delhi', 'state': 'Delhi', 'pincode': '110002',
                'delivery_radius': 25, 'minimum_order_amount': 300, 'delivery_charge': 30
            },
        ]
        
        vendors = []
        suppliers = []
        
        for user_data in users_data:
            user_type = user_data.pop('user_type')
            business_name = user_data.pop('business_name')
            business_type = user_data.pop('business_type')
            
            if user_type == 'supplier':
                delivery_radius = user_data.pop('delivery_radius')
                minimum_order_amount = user_data.pop('minimum_order_amount')
                delivery_charge = user_data.pop('delivery_charge')
            
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                
                if user_type == 'vendor':
                    profile = VendorProfile.objects.create(
                        user=user,
                        business_name=business_name,
                        business_type=business_type
                    )
                    vendors.append(profile)
                    self.stdout.write(f'Created vendor: {profile.business_name}')
                else:
                    profile = SupplierProfile.objects.create(
                        user=user,
                        business_name=business_name,
                        business_type=business_type,
                        delivery_radius=delivery_radius,
                        minimum_order_amount=minimum_order_amount,
                        delivery_charge=delivery_charge
                    )
                    suppliers.append(profile)
                    self.stdout.write(f'Created supplier: {profile.business_name}')
        
        # Create supplier products
        supplier_products = []
        for supplier in suppliers:
            for product in random.sample(products, 5):  # Each supplier has 5 random products
                price = Decimal(random.uniform(20, 200))
                stock = Decimal(random.uniform(10, 100))
                
                supplier_product, created = SupplierProduct.objects.get_or_create(
                    supplier=supplier,
                    product=product,
                    defaults={
                        'price': price,
                        'stock_quantity': stock,
                        'minimum_order_quantity': 1,
                        'is_available': True,
                        'description': f'Quality {product.name} from {supplier.business_name}'
                    }
                )
                supplier_products.append(supplier_product)
                if created:
                    self.stdout.write(f'Created supplier product: {supplier.business_name} - {product.name}')
        
        # Create some reviews
        for vendor in vendors:
            for supplier in suppliers:
                if random.choice([True, False]):  # 50% chance of review
                    review, created = Review.objects.get_or_create(
                        vendor=vendor,
                        supplier=supplier,
                        defaults={
                            'rating': random.randint(3, 5),
                            'title': f'Great service from {supplier.business_name}',
                            'comment': f'Excellent quality products and timely delivery. Highly recommended!',
                            'is_verified_purchase': True
                        }
                    )
                    if created:
                        self.stdout.write(f'Created review: {vendor.business_name} -> {supplier.business_name}')
        
        # Create some orders
        for vendor in vendors:
            for supplier in suppliers:
                if random.choice([True, False]):  # 50% chance of order
                    order = Order.objects.create(
                        vendor=vendor,
                        supplier=supplier,
                        status=random.choice(['pending', 'confirmed', 'delivered']),
                        delivery_address=vendor.user.address,
                        payment_method='cash_on_delivery',
                        payment_status='pending'
                    )
                    
                    # Add order items
                    supplier_products_for_supplier = [sp for sp in supplier_products if sp.supplier == supplier]
                    if supplier_products_for_supplier:
                        selected_products = random.sample(supplier_products_for_supplier, random.randint(1, 3))
                        total_amount = Decimal('0')
                        
                        for sp in selected_products:
                            quantity = Decimal(random.uniform(1, 10))
                            unit_price = sp.price
                            total_price = quantity * unit_price
                            total_amount += total_price
                            
                            OrderItem.objects.create(
                                order=order,
                                supplier_product=sp,
                                quantity=quantity,
                                unit_price=unit_price,
                                total_price=total_price
                            )
                        
                        order.total_amount = total_amount + supplier.delivery_charge
                        order.save()
                        
                        # Create status history
                        OrderStatusHistory.objects.create(
                            order=order,
                            status=order.status,
                            notes='Order created'
                        )
                        
                        self.stdout.write(f'Created order: {order.order_id} - {vendor.business_name} -> {supplier.business_name}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(f'Created {len(categories)} categories')
        self.stdout.write(f'Created {len(products)} products')
        self.stdout.write(f'Created {len(vendors)} vendors')
        self.stdout.write(f'Created {len(suppliers)} suppliers')
        self.stdout.write(f'Created {len(supplier_products)} supplier products')
        self.stdout.write(f'Created {Review.objects.count()} reviews')
        self.stdout.write(f'Created {Order.objects.count()} orders')
