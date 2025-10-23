from rest_framework import serializers
from .models import Review, ProductReview, ReviewImage
from accounts.serializers import VendorProfileSerializer, SupplierProfileSerializer
from products.serializers import ProductSerializer

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    vendor = VendorProfileSerializer(read_only=True)
    supplier = SupplierProfileSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['supplier', 'rating', 'title', 'comment']

class ProductReviewSerializer(serializers.ModelSerializer):
    vendor = VendorProfileSerializer(read_only=True)
    supplier = SupplierProfileSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductReview
        fields = '__all__'

class ProductReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['supplier', 'product', 'rating', 'comment']

class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']

class ProductReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']

class SupplierReviewSummarySerializer(serializers.Serializer):
    supplier_id = serializers.IntegerField()
    supplier_name = serializers.CharField()
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField()  # {1: count, 2: count, ...}

class ProductReviewSummarySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField()
