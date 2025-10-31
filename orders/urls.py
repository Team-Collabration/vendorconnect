from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('api/nearby/', views.nearby_suppliers, name='nearby_suppliers'),
    path('supplier/save_location/', views.save_supplier_location, name='save_supplier_location'),
    path('quick-order/<int:supplier_product_id>/', views.create_quick_order, name='quick-order'),
    path('create/', views.create_order, name='create-order'),  # Make sure this exists
    # API endpoints for orders
    path('api/create/', views.create_order, name='create_order'),
    path('api/vendor/orders/', views.vendor_orders, name='vendor_orders_api'),
    path('api/supplier/orders/', views.supplier_orders, name='supplier_orders_api'),
    path('api/supplier/orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),

    # Supplier order management
    path('supplier/orders/', views.supplier_orders, name='supplier-orders'),
    path('supplier/orders/<int:order_id>/update-status/', views.update_order_status, name='update-order-status'),
    path('api/supplier/analytics/', views.supplier_analytics, name='supplier_analytics'),

    # Vendor order tracking
    path('vendor/orders/', views.vendor_orders, name='vendor-orders'),
    # ... your existing URL patterns ...
    path('products/api/supplier-products/', views.get_supplier_products, name='supplier_products'),
    # Notification URLs
    path('api/notifications/get/', views.get_notifications, name='get_notifications'),
    path('api/notifications/unread-count/', views.get_unread_count, name='get_unread_count'),
    path('api/notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('api/notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('api/notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),

]