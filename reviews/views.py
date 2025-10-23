from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Avg, Count
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer,
    ProductReviewSerializer, ProductReviewCreateSerializer, ProductReviewUpdateSerializer,
    SupplierReviewSummarySerializer, ProductReviewSummarySerializer
)
from .models import Review, ProductReview, ReviewImage
from orders.models import VendorProfile, SupplierProfile
from products.models import Product

class ReviewListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        supplier_id = self.request.query_params.get('supplier_id')
        if supplier_id:
            return Review.objects.filter(supplier_id=supplier_id)
        return Review.objects.all()

class ReviewDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

class ReviewCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewCreateSerializer
    
    def perform_create(self, serializer):
        # Ensure the user is a vendor
        if not hasattr(self.request.user, 'vendor_profile'):
            raise permissions.PermissionDenied("Only vendors can create reviews")
        
        serializer.save(vendor=self.request.user.vendor_profile)

class ReviewUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewUpdateSerializer
    
    def get_queryset(self):
        # Only allow vendors to update their own reviews
        return Review.objects.filter(vendor__user=self.request.user)

class ReviewDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only allow vendors to delete their own reviews
        return Review.objects.filter(vendor__user=self.request.user)

class ProductReviewListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductReviewSerializer
    
    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        supplier_id = self.request.query_params.get('supplier_id')
        
        queryset = ProductReview.objects.all()
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        
        return queryset

class ProductReviewDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductReviewSerializer
    queryset = ProductReview.objects.all()

class ProductReviewCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductReviewCreateSerializer
    
    def perform_create(self, serializer):
        # Ensure the user is a vendor
        if not hasattr(self.request.user, 'vendor_profile'):
            raise permissions.PermissionDenied("Only vendors can create product reviews")
        
        serializer.save(vendor=self.request.user.vendor_profile)

class ProductReviewUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductReviewUpdateSerializer
    
    def get_queryset(self):
        # Only allow vendors to update their own product reviews
        return ProductReview.objects.filter(vendor__user=self.request.user)

class ProductReviewDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only allow vendors to delete their own product reviews
        return ProductReview.objects.filter(vendor__user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def supplier_reviews_summary(request, supplier_id):
    """Get summary of reviews for a supplier"""
    try:
        supplier = SupplierProfile.objects.get(id=supplier_id)
        reviews = Review.objects.filter(supplier=supplier)
        
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            total_reviews = reviews.count()
            
            # Calculate rating distribution
            rating_distribution = {}
            for i in range(1, 6):
                rating_distribution[i] = reviews.filter(rating=i).count()
            
            summary = {
                'supplier_id': supplier.id,
                'supplier_name': supplier.business_name,
                'average_rating': round(avg_rating, 2),
                'total_reviews': total_reviews,
                'rating_distribution': rating_distribution
            }
        else:
            summary = {
                'supplier_id': supplier.id,
                'supplier_name': supplier.business_name,
                'average_rating': 0,
                'total_reviews': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        return Response(summary)
        
    except SupplierProfile.DoesNotExist:
        return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_reviews_summary(request, product_id):
    """Get summary of reviews for a product"""
    try:
        product = Product.objects.get(id=product_id)
        reviews = ProductReview.objects.filter(product=product)
        
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            total_reviews = reviews.count()
            
            # Calculate rating distribution
            rating_distribution = {}
            for i in range(1, 6):
                rating_distribution[i] = reviews.filter(rating=i).count()
            
            summary = {
                'product_id': product.id,
                'product_name': product.name,
                'average_rating': round(avg_rating, 2),
                'total_reviews': total_reviews,
                'rating_distribution': rating_distribution
            }
        else:
            summary = {
                'product_id': product.id,
                'product_name': product.name,
                'average_rating': 0,
                'total_reviews': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        return Response(summary)
        
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_reviews(request):
    """Get reviews created by the current user"""
    user = request.user
    
    if hasattr(user, 'vendor_profile'):
        reviews = Review.objects.filter(vendor=user.vendor_profile)
        product_reviews = ProductReview.objects.filter(vendor=user.vendor_profile)
        
        return Response({
            'supplier_reviews': ReviewSerializer(reviews, many=True).data,
            'product_reviews': ProductReviewSerializer(product_reviews, many=True).data
        })
    else:
        return Response({'error': 'Only vendors can have reviews'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def supplier_reviews_analytics(request):
    """Get analytics for supplier reviews (for suppliers)"""
    user = request.user
    
    if not hasattr(user, 'supplier_profile'):
        return Response({'error': 'Only suppliers can access this'}, status=status.HTTP_400_BAD_REQUEST)
    
    reviews = Review.objects.filter(supplier=user.supplier_profile)
    
    if reviews.exists():
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        total_reviews = reviews.count()
        
        # Rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[i] = reviews.filter(rating=i).count()
        
        # Recent reviews
        recent_reviews = reviews.order_by('-created_at')[:5]
        
        analytics = {
            'average_rating': round(avg_rating, 2),
            'total_reviews': total_reviews,
            'rating_distribution': rating_distribution,
            'recent_reviews': ReviewSerializer(recent_reviews, many=True).data
        }
    else:
        analytics = {
            'average_rating': 0,
            'total_reviews': 0,
            'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'recent_reviews': []
        }
    
    return Response(analytics)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_review_image(request, review_id):
    """Upload image for a review"""
    try:
        user = request.user
        
        if hasattr(user, 'vendor_profile'):
            review = Review.objects.get(id=review_id, vendor=user.vendor_profile)
        else:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        image_file = request.FILES.get('image')
        caption = request.data.get('caption', '')
        
        if not image_file:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        ReviewImage.objects.create(
            review=review,
            image=image_file,
            caption=caption
        )
        
        return Response({'message': 'Image uploaded successfully'})
        
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
