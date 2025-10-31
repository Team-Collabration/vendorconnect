from django.urls import path
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # ==================== Category URLs ====================
    path('categories/', 
         views.CategoryListView.as_view(), 
         name='category-list'),
    path('categories/<int:pk>/', 
         views.CategoryDetailView.as_view(), 
         name='category-detail'),
    path('categories-summary/', 
         views.product_categories, 
         name='product-categories'),
    
    # ==================== Product URLs ====================
    path('products/', 
         views.ProductListView.as_view(), 
         name='product-list'),
    path('products/<int:pk>/', 
         views.ProductDetailView.as_view(), 
         name='product-detail'),
    
    # ==================== Supplier Product URLs ====================
    # List all available supplier products (public)
    path('supplier-products/', 
         views.SupplierProductListView.as_view(), 
         name='supplier-product-list'),
    
    # Get single supplier product details
    path('supplier-products/<int:pk>/', 
         views.SupplierProductDetailView.as_view(), 
         name='supplier-product-detail'),
    
    # Create new supplier product (authenticated suppliers only)
    path('supplier-products/create/', 
         views.SupplierProductCreateView.as_view(), 
         name='supplier-product-create'),
    
    # Update supplier product (authenticated suppliers only - their own products)
    path('supplier-products/<int:pk>/update/', 
         views.SupplierProductUpdateView.as_view(), 
         name='supplier-product-update'),
    
    # Delete supplier product (authenticated suppliers only - their own products)
    path('supplier-products/<int:pk>/delete/', 
         views.SupplierProductDeleteView.as_view(), 
         name='supplier-product-delete'),
    
    # ==================== My Products URLs ====================
    # Get logged-in supplier's own products
    path('my-supplier-products/', 
         views.MySupplierProductsView.as_view(), 
         name='my-supplier-products'),
    
    # ==================== Search & Filter URLs ====================
    # Advanced product search
    path('search/', 
         views.ProductSearchView.as_view(), 
         name='product-search'),
    
    # ==================== Supplier Specific URLs ====================
    # Get all products from a specific supplier
    path('suppliers/<int:supplier_id>/products/', 
         views.SupplierProductsView.as_view(), 
         name='supplier-products'),
    
    # Get summary of supplier's products
    path('suppliers/<int:supplier_id>/products-summary/', 
         views.supplier_products_summary, 
         name='supplier-products-summary'),
   


    path('debug-data/', views.debug_data, name='debug-data'),
    path('save_location/', views.save_location, name='save_location'),
    path('get_location/', views.get_location, name='get_location'),
    
    #path('compare-prices/', views.compareprices, name='compareprices'),
    path('api/compare-prices/', views.compare_prices_api, name='compare-prices-api'),

]

