from django.db import models
from django.contrib.auth.models import User
from django.conf import settings 

class Supplier(models.Model):
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # use this instead of auth.User
        on_delete=models.CASCADE,
        
    )
    name = models.CharField(max_length=200)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    items = models.TextField(blank=True)
    price = models.FloatField(blank=True, null=True)
class VendorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # use this instead of auth.User
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )

    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    preferred_supply_schedule = models.CharField(max_length=50, blank=True, null=True)
   
class SupplierProfile(models.Model):
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # use this instead of auth.User
        on_delete=models.CASCADE,
        related_name='supplier_profile'
    )
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    delivery_radius = models.IntegerField(default=50)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone = models.CharField(max_length=20, blank=True, null=True) 
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
    
    
# Add this to your existing models

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_orders'
    )
    supplier = models.ForeignKey(
        SupplierProfile,
        on_delete=models.CASCADE,
        related_name='received_orders'
    )
    supplier_product = models.ForeignKey(
        'products.SupplierProduct',
        on_delete=models.CASCADE
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    delivery_address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    expected_delivery_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.vendor.username} from {self.supplier.business_name}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
