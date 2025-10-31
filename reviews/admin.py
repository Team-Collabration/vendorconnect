from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'supplier', 'get_product_name', 'rating', 'get_is_verified', 'created_at']
    list_filter = ['rating', 'created_at']  # Remove is_verified if it's not a real field
    search_fields = ['vendor__user__username', 'supplier__business_name', 'product_name', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Review Information', {
            'fields': ('vendor', 'supplier', 'order')
        }),
        ('Product & Rating', {
            'fields': ('product_name', 'rating', 'comment')
        }),
        ('Status', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_product_name(self, obj):
        return obj.product_name  # Only if it exists
    get_product_name.short_description = 'Product Name'
    
    def get_is_verified(self, obj):
        return getattr(obj, 'is_verified', False)  # Safe fallback
    get_is_verified.boolean = True
    get_is_verified.short_description = 'Verified'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('vendor', 'supplier', 'order')
