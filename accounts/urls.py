from django.urls import path,include
from . import views

urlpatterns = [
    # Supplier
    path("supplier/signup/", views.supplier_signup_template, name="suppliersignup"),
    path("supplier/dashboard/", views.supplier_dashboard_template, name="suppliers-dashboard"),

    # Vendor
    path("vendor/signup/", views.vendorsignup_template, name="vendorsignup"),
    path("vendor/dashboard/", views.vendor_dashboard_template, name="vendordashboard"),

    # Login / Logout
    path("vendor/login/", views.vendor_login, name="vendorlogin"),
    path("supplier/login/", views.supplier_login, name="supplierlogin"),
    path("logout/", views.logout_view, name="logout"),

    # OTP
    # OTP
    path("send_email_otp/", views.send_email_otp, name="send_email_otp"),
    path("verify_email_otp/", views.verify_email_otp, name="verify_email_otp"),

    # Google OAuth
    path('accounts/google-signup/', views.google_signup, name='google_signup'),
    path('accounts/google-redirect/', views.google_redirect, name='google_redirect'),

    # Allauth
    path('accounts/', include('allauth.urls')),
   path('profile/view/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('supplier/save_location/', views.save_supplier_location, name='save_supplier_location'),
    path('supplier/get_location/', views.get_supplier_location, name='get_supplier_location'),
    path('api/all_suppliers/', views.get_all_suppliers, name='all_suppliers'),
    path('api/nearby/', views.get_nearby_suppliers, name='nearby_suppliers'),
    
    path('create-payment/', views.create_payment, name='create_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),


]