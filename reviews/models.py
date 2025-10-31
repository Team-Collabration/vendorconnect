from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from orders.models import VendorProfile, SupplierProfile
from products.models import Product
from django.conf import settings
User=settings.AUTH_USER_MODEL
class Review(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='reviews_given')
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='reviews_received')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)  # ✅ Add this
    product_name = models.CharField(max_length=200, blank=True, null=True)  # ✅ Add this
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, default='Review')  # ✅ Add default
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ✅ Changed unique_together to allow multiple reviews per vendor-supplier (one per order)
        unique_together = ['vendor', 'supplier', 'order']

    def __str__(self):
        return f"{self.vendor.business_name} -> {self.supplier.business_name} ({self.rating}★)"

class ProductReview(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='product_reviews_given')
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='product_reviews_received')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.vendor.business_name} -> {self.product.name} ({self.rating}★)"

class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images', blank=True, null=True)
    product_review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='images', blank=True, null=True)
    image = models.ImageField(upload_to='review_images/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review Image - {self.uploaded_at}"
    
from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"