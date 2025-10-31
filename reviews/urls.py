from django.urls import path
from . import views

urlpatterns = [
    # Main review page
    path('', views.leave_reviews_page, name='leavereviews'),
    
    # Web views (HTML pages)
    path('suppliers-dashboard/', views.supplier_dashboard_reviews, name='supplier_dashboard_reviews'),
    path('submit-review/', views.submit_review, name='submit_review'),
    
    # API endpoint for fetching vendor orders
    path('vendor-orders/', views.get_vendor_orders, name='vendor_orders'),
    
    # Reviews API
    path('api/reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('api/reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('api/reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('api/reviews/<int:pk>/update/', views.ReviewUpdateView.as_view(), name='review-update'),
    path('api/reviews/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
    
    # Product Reviews API
    path('api/product-reviews/', views.ProductReviewListView.as_view(), name='product-review-list'),
    path('api/product-reviews/<int:pk>/', views.ProductReviewDetailView.as_view(), name='product-review-detail'),
    path('api/product-reviews/create/', views.ProductReviewCreateView.as_view(), name='product-review-create'),
    path('api/product-reviews/<int:pk>/update/', views.ProductReviewUpdateView.as_view(), name='product-review-update'),
    path('api/product-reviews/<int:pk>/delete/', views.ProductReviewDeleteView.as_view(), name='product-review-delete'),
    path('supplier/reviews/', views.supplier_dashboard_reviews, name='supplier_reviews'),  # ✅ ADD THIS
    # Analytics and summaries
    path('api/suppliers/<int:supplier_id>/reviews-summary/', views.supplier_reviews_summary, name='supplier-reviews-summary'),
    path('api/products/<int:product_id>/reviews-summary/', views.product_reviews_summary, name='product-reviews-summary'),
    path('api/my-reviews/', views.my_reviews, name='my-reviews'),
    path('api/supplier-reviews-analytics/', views.supplier_reviews_analytics, name='supplier-reviews-analytics'),
    
    # Review images
    path('api/reviews/<int:review_id>/upload-image/', views.upload_review_image, name='upload-review-image'),
]