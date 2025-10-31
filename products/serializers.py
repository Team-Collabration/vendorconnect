from rest_framework import serializers
from .models import Category, Product, SupplierProduct
from accounts.serializers import SupplierProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    product_count = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'created_at', 'product_count']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.IntegerField(source='category.id', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'category_id',
            'description', 'unit', 'unit_display', 'image', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SupplierProductSerializer(serializers.ModelSerializer):
    """Serializer for SupplierProduct model with nested relations"""
    product = ProductSerializer(read_only=True)
    supplier = SupplierProfileSerializer(read_only=True)
    
    # ADD THIS - Explicit supplier_id field
    supplier_id = serializers.IntegerField(source='supplier.id', read_only=True)
    
    # Convenience fields
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    unit = serializers.CharField(source='product.unit', read_only=True)
    unit_display = serializers.CharField(source='product.get_unit_display', read_only=True)
    supplier_name = serializers.CharField(source='supplier.business_name', read_only=True)
    
    # Calculated fields
    total_value = serializers.SerializerMethodField()
    
    class Meta:
        model = SupplierProduct
        fields = [
            'id', 'supplier', 'supplier_id', 'supplier_name', 'product', 'product_name',
            'category_name', 'unit', 'unit_display', 'price', 'stock_quantity',
            'minimum_order_quantity', 'is_available', 'description',
            'total_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_value(self, obj):
        """Calculate total value of stock (price * quantity)"""
        return float(obj.price * obj.stock_quantity)
    
    
    
class SupplierProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SupplierProduct (simpler version)"""
    product_name = serializers.CharField(write_only=True, required=False)
    category_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = SupplierProduct
        fields = [
            'product', 'product_name', 'category_name', 'price', 
            'stock_quantity', 'minimum_order_quantity', 'is_available', 'description'
        ]
    
    def validate_price(self, value):
        """Ensure price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_stock_quantity(self, value):
        """Ensure stock quantity is not negative"""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative")
        return value


class SupplierProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating SupplierProduct"""
    
    class Meta:
        model = SupplierProduct
        fields = [
            'price', 'stock_quantity', 'minimum_order_quantity', 
            'is_available', 'description'
        ]
    
    def validate_price(self, value):
        """Ensure price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_stock_quantity(self, value):
        """Ensure stock quantity is not negative"""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative")
        return value


class ProductSearchSerializer(serializers.Serializer):
    """Serializer for product search parameters"""
    query = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Search by product name or description"
    )
    category = serializers.IntegerField(
        required=False,
        help_text="Filter by category ID"
    )
    min_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        help_text="Minimum price filter"
    )
    max_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        help_text="Maximum price filter"
    )
    supplier_id = serializers.IntegerField(
        required=False,
        help_text="Filter by supplier ID"
    )
    location_lat = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False,
        help_text="Latitude for location-based search"
    )
    location_lng = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False,
        help_text="Longitude for location-based search"
    )
    radius = serializers.IntegerField(
        default=50, 
        required=False,
        help_text="Search radius in kilometers"
    )
    
    def validate(self, data):
        """Validate search parameters"""
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError(
                "min_price cannot be greater than max_price"
            )
        
        location_lat = data.get('location_lat')
        location_lng = data.get('location_lng')
        
        if (location_lat and not location_lng) or (location_lng and not location_lat):
            raise serializers.ValidationError(
                "Both location_lat and location_lng must be provided together"
            )
        
        return data


class SupplierProductSimpleSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing products (better performance)"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.business_name', read_only=True)
    
    class Meta:
        model = SupplierProduct
        fields = [
            'id', 'product_name', 'category_name', 'supplier_name',
            'price', 'stock_quantity', 'is_available'
        ]