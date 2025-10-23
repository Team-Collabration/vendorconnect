from django.urls import path
from . import views

urlpatterns = [
    # Reviews
    path('reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:pk>/update/', views.ReviewUpdateView.as_view(), name='review-update'),
    path('reviews/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
    
    # Product Reviews
    path('product-reviews/', views.ProductReviewListView.as_view(), name='product-review-list'),
    path('product-reviews/<int:pk>/', views.ProductReviewDetailView.as_view(), name='product-review-detail'),
    path('product-reviews/create/', views.ProductReviewCreateView.as_view(), name='product-review-create'),
    path('product-reviews/<int:pk>/update/', views.ProductReviewUpdateView.as_view(), name='product-review-update'),
    path('product-reviews/<int:pk>/delete/', views.ProductReviewDeleteView.as_view(), name='product-review-delete'),
    
    # Analytics and summaries
    path('suppliers/<int:supplier_id>/reviews-summary/', views.supplier_reviews_summary, name='supplier-reviews-summary'),
    path('products/<int:product_id>/reviews-summary/', views.product_reviews_summary, name='product-reviews-summary'),
    path('my-reviews/', views.my_reviews, name='my-reviews'),
    path('supplier-reviews-analytics/', views.supplier_reviews_analytics, name='supplier-reviews-analytics'),
    
    # Review images
    path('reviews/<int:review_id>/upload-image/', views.upload_review_image, name='upload-review-image'),
]
