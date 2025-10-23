"""
URL configuration for vendorconnect_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views



urlpatterns = [
    # Frontend routes
    path('', views.index_template, name='index'),  # root URL
    path('vendor/login/', views.vendorlogin_template, name='vendorlogin'),
    path('supplier/login/', views.supplierlogin_template, name='supplierlogin'),
    path('vendorsignup/', views.vendorsignup_template, name='vendorsignup'),
    path('suppliersignup/', views.suppliersignup_template, name='suppliersignup'),
    path('about/', views.about_template, name='about'),
     path('contact/', views.contact, name='contact'),
    path('suppliers/', views.suppliers_template, name='suppliers'),
    path('suppliers-dashboard/', views.suppliers_dashboard_template, name='suppliers_dashboard'),
    path('listproducts/', views.listproducts_template, name='listproducts'),
    path('manageorders/', views.manageorders_template, name='manageorders'),
    path('analytics/', views.analytics_template, name='analytics'),
    path('support/', views.support_template, name='support'),
    path('vendordashboard/', views.vendor_dashboard_template, name='vendor_dashboard'),
    path('orders/', views.vendor_orders_template, name='orders'),
    path('findsuppliers/', views.findsuppliers_template, name='findsuppliers'),
    # path('admin/', admin.site.urls),
    # path('', include('orders.urls')),
    path('api/chat/', include('chatbot.urls')),  # ✅ this connects the chatbot routes
    path('chat/', include('chat.urls')),  # 👈 This connects /chat/ to your chat app
    path('compareprices/', views.compareprices_template, name='compareprices'),
    path('leavereviews/', views.reviews_template, name='leavereviews'),
    path('bulk/', views.bulk_template, name='bulk'),
    path("bulk-order/", views.place_bulk_order, name="place_bulk_order"),  # to process form
    # path('api/ai-response/', views.ai_response_view, name='ai_response'),
     path('api/all_suppliers/', views.all_suppliers, name='all_suppliers'),
     path('supplier/save_location/', views.save_supplier_location, name='save_supplier_location'),
    path("chatbot/",include("chatbot.urls")),
    # Admin and APIs
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
   path('', include('orders.urls')),  # for frontend URLs like /supplier/orders/

    path('api/reviews/', include('reviews.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
