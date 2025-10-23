from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, SupplierProduct


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'unit']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = [
        'supplier', 
        'product', 
        'price', 
        'stock_quantity', 
        'is_available', 
        'created_at'
    ]
    list_filter = ['is_available', 'product__category', 'created_at']
    search_fields = [
        'supplier__business_name', 
        'supplier__user__username',
        'product__name'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Supplier & Product', {
            'fields': ('supplier', 'product')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity', 'minimum_order_quantity', 'is_available')
        }),
        ('Additional Info', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )