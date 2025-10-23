from django.db import models
from orders.models import SupplierProfile


class Category(models.Model):
    """Product categories (Vegetables, Fruits, Dairy, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # FontAwesome icon class
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Base product model (product definitions)"""
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Liter'),
        ('ml', 'Milliliter'),
        ('pcs', 'Pieces'),
        ('dozen', 'Dozen'),
        ('pack', 'Pack'),
        ('bundle', 'Bundle'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"


class SupplierProduct(models.Model):
    """Products offered by suppliers with their specific pricing"""
    supplier = models.ForeignKey(
        SupplierProfile, 
        on_delete=models.CASCADE, 
        related_name='supplier_products'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='supplier_products'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_order_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    is_available = models.BooleanField(default=True)
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional description or notes about this product from the supplier"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['supplier', 'product']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['supplier', 'is_available']),
            models.Index(fields=['product', 'is_available']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        return f"{self.supplier.business_name} - {self.product.name} (₹{self.price})"
    
    @property
    def total_value(self):
        """Calculate total value of available stock"""
        return self.price * self.stock_quantity
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity (for order processing)"""
        if quantity > self.stock_quantity:
            raise ValueError("Insufficient stock")
        self.stock_quantity -= quantity
        self.save()
    
    def add_stock(self, quantity):
        """Add stock quantity"""
        self.stock_quantity += quantity
        self.save()