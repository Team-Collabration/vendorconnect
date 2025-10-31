from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Avg, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer,
    ProductReviewSerializer, ProductReviewCreateSerializer, ProductReviewUpdateSerializer,
    SupplierReviewSummarySerializer, ProductReviewSummarySerializer
)
from .models import Review, ProductReview, ReviewImage
from orders.models import VendorProfile, SupplierProfile, Order
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

# ========== TEMPLATE FILTER ==========
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get dictionary item by key
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return 0
    try:
        return dictionary.get(int(key), 0)
    except (ValueError, TypeError, AttributeError):
        return 0
from django.contrib import messages
# ========== WEB VIEWS (HTML Pages) ==========
@login_required
def leave_reviews_page(request):
    print("\n" + "="*80)
    print("🔍 DEBUGGING leave_reviews_page")
    print("="*80)
    
    print(f"\n👤 USER INFO:")
    print(f"   User ID: {request.user.id}")
    print(f"   Username: '{request.user.username}'")
    print(f"   Email: {request.user.email}")
    print(f"   User type: {request.user.user_type}")
    
    # Get vendor profile
    from orders.models import VendorProfile
    vendor = None
    
    try:
        vendor = VendorProfile.objects.get(user=request.user)
        print(f"\n✅ VendorProfile found: {vendor.business_name} (ID: {vendor.id})")
    except VendorProfile.DoesNotExist:
        print(f"\n❌ No VendorProfile found for user ID {request.user.id}")
        
        # Check all vendor profiles
        all_vendors = VendorProfile.objects.all()
        print(f"\n📊 All VendorProfiles in database ({all_vendors.count()}):")
        for v in all_vendors:
            print(f"   - ID: {v.id}, Business: {v.business_name}, User ID: {v.user_id}, Username: '{v.user.username}'")
        
        # Create one
        vendor = VendorProfile.objects.create(
            user=request.user,
            business_name=request.user.email.split('@')[0] if request.user.email else f"Vendor_{request.user.id}"
        )
        print(f"\n🔧 Created VendorProfile: {vendor.business_name}")
    
    # Check ALL orders in the system
    print(f"\n\n📦 ALL ORDERS IN DATABASE:")
    all_system_orders = Order.objects.all().select_related('vendor', 'supplier')
    print(f"   Total orders: {all_system_orders.count()}")
    for order in all_system_orders:
        print(f"   Order #{order.id}:")
        print(f"      - Vendor User ID: {order.vendor_id}")
        print(f"      - Vendor Username: '{order.vendor.username}'")
        print(f"      - Supplier: {order.supplier.business_name} (ID: {order.supplier_id})")
        print(f"      - Status: '{order.status}'")
        print(f"      - Product: {order.supplier_product.product.name}")
    
    # Check orders for THIS user
    print(f"\n\n📦 ORDERS FOR CURRENT USER (ID: {request.user.id}):")
    user_orders = Order.objects.filter(vendor=request.user).select_related('supplier', 'supplier_product__product')
    print(f"   Found: {user_orders.count()} orders")
    
    for order in user_orders:
        print(f"   Order #{order.id}: Status='{order.status}', Supplier={order.supplier.business_name}")
    
    if user_orders.count() == 0:
        print(f"\n⚠️  NO ORDERS FOUND FOR USER ID {request.user.id}")
        print(f"   Checking if vendor_id matches any orders...")
        orders_by_vendor_id = Order.objects.filter(vendor_id=request.user.id)
        print(f"   Orders with vendor_id={request.user.id}: {orders_by_vendor_id.count()}")
    
    # Check for ALL possible status values
    print(f"\n\n🔍 CHECKING ALL STATUS VALUES:")
    all_statuses = Order.objects.filter(vendor=request.user).values_list('status', flat=True).distinct()
    print(f"   Statuses in orders: {list(all_statuses)}")
    
    # Try different status filters
    print(f"\n   Testing different status filters:")
    print(f"      - 'completed': {Order.objects.filter(vendor=request.user, status='completed').count()}")
    print(f"      - 'Completed': {Order.objects.filter(vendor=request.user, status='Completed').count()}")
    print(f"      - 'confirmed': {Order.objects.filter(vendor=request.user, status='confirmed').count()}")
    print(f"      - 'Confirmed': {Order.objects.filter(vendor=request.user, status='Confirmed').count()}")
    print(f"      - 'shipped': {Order.objects.filter(vendor=request.user, status='shipped').count()}")
    print(f"      - 'Shipped': {Order.objects.filter(vendor=request.user, status='Shipped').count()}")
    print(f"      - 'delivered': {Order.objects.filter(vendor=request.user, status='delivered').count()}")
    print(f"      - 'Delivered': {Order.objects.filter(vendor=request.user, status='Delivered').count()}")
    
    # Get completed orders - Try multiple statuses
    completed_orders = Order.objects.filter(
        vendor=request.user,
        status__in=['completed', 'Completed', 'delivered', 'Delivered']
    )
    
    print(f"\n\n✅ Orders with completed/delivered status: {completed_orders.count()}")
    for order in completed_orders:
        print(f"   Order #{order.id}: Supplier={order.supplier.business_name} (ID: {order.supplier_id})")
    
    # Get unique supplier IDs
    completed_order_supplier_ids = list(completed_orders.values_list('supplier_id', flat=True).distinct())
    print(f"\n📋 Unique supplier IDs from completed orders: {completed_order_supplier_ids}")
    
    # Get suppliers
    suppliers = SupplierProfile.objects.filter(id__in=completed_order_supplier_ids)
    print(f"\n🏢 Suppliers to show in dropdown: {suppliers.count()}")
    for supplier in suppliers:
        print(f"   - {supplier.business_name} (ID: {supplier.id})")
    
    # If still no suppliers, let's be more lenient
    if suppliers.count() == 0:
        print(f"\n⚠️  No suppliers found with completed/delivered status")
        print(f"   Let's try getting suppliers from ANY order status...")
        
        # Get suppliers from ALL orders (any status)
        all_order_supplier_ids = list(user_orders.values_list('supplier_id', flat=True).distinct())
        print(f"   Supplier IDs from all orders: {all_order_supplier_ids}")
        
        suppliers = SupplierProfile.objects.filter(id__in=all_order_supplier_ids)
        print(f"   Suppliers from all orders: {suppliers.count()}")
        for supplier in suppliers:
            print(f"      - {supplier.business_name} (ID: {supplier.id})")
    
    suppliers_with_orders = set(completed_order_supplier_ids)
    
    context = {
        'suppliers': suppliers,
        'vendor': vendor,
        'suppliers_with_orders': suppliers_with_orders
    }
    
    print(f"\n🎯 FINAL CONTEXT:")
    print(f"   - suppliers count: {suppliers.count()}")
    print(f"   - suppliers_with_orders: {suppliers_with_orders}")
    print("="*80 + "\n")
    
    return render(request, 'leavereviews.html', context)
@login_required
def supplier_dashboard_reviews(request):
    """Supplier dashboard to view their received reviews"""
    # Get supplier profile
    try:
        supplier = SupplierProfile.objects.get(user=request.user)
    except SupplierProfile.DoesNotExist:
        messages.error(request, 'Supplier profile not found')
        return redirect('suppliers-dashboard')
    
    print(f"\n🔍 Loading reviews for supplier: {supplier.business_name}")
    
    # Get all reviews for this supplier
    reviews = Review.objects.filter(supplier=supplier).select_related('vendor', 'order').order_by('-created_at')
    
    print(f"   Found {reviews.count()} reviews")
    
    # Calculate statistics
    if reviews.exists():
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        total_reviews = reviews.count()
        
        rating_distribution = {}
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            rating_distribution[i] = count
            print(f"   {i} stars: {count} reviews")
    else:
        avg_rating = 0
        total_reviews = 0
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        print("   No reviews yet")
    
    context = {
        'reviews': reviews,
        'average_rating': round(avg_rating, 2) if avg_rating else 0,
        'total_reviews': total_reviews,
        'rating_distribution': rating_distribution,
        'supplier': supplier
    }
    
    return render(request, 'supplier_reviews.html', context)

@login_required
def submit_review(request):
    """Handle review submission from vendor"""
    if request.method == 'POST':
        if not hasattr(request.user, 'vendor_profile'):
            try:
                vendor = VendorProfile.objects.get(user=request.user)
            except VendorProfile.DoesNotExist:
                messages.error(request, 'Only vendors can submit reviews')
                return redirect('leavereviews')
        else:
            vendor = request.user.vendor_profile
        
        supplier_id = request.POST.get('supplier')
        order_id = request.POST.get('order_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        print("\n" + "="*50)
        print("📝 REVIEW SUBMISSION DEBUG")
        print("="*50)
        print(f"Vendor: {vendor.business_name}")
        print(f"Supplier ID: {supplier_id}")
        print(f"Order ID: {order_id}")
        print(f"Rating: {rating}")
        print(f"Comment: {comment}")
        
        try:
            # Validate inputs
            if not all([supplier_id, rating, comment]):
                messages.error(request, 'Supplier, rating, and comment are required')
                return redirect('leavereviews')
            
            # Get supplier
            supplier = SupplierProfile.objects.get(id=supplier_id)
            print(f"✅ Supplier found: {supplier.business_name}")
            
            # Get order if provided
            order = None
            if order_id:
                try:
                    order = Order.objects.get(
                        id=order_id,
                        vendor=request.user,
                        supplier=supplier
                    )
                    print(f"✅ Order found: #{order.id}")
                except Order.DoesNotExist:
                    print(f"⚠️  Order #{order_id} not found, creating review without order")
            
            # Check if review already exists for this order
            if order:
                existing_review = Review.objects.filter(
                    vendor=vendor,
                    supplier=supplier,
                    order=order
                ).first()
            else:
                # If no order specified, check if review exists for this vendor-supplier pair without order
                existing_review = Review.objects.filter(
                    vendor=vendor,
                    supplier=supplier,
                    order__isnull=True
                ).first()
            
            if existing_review:
                # Update existing review
                existing_review.rating = int(rating)
                existing_review.comment = comment
                existing_review.save()
                print(f"✅ Updated existing review ID: {existing_review.id}")
                messages.success(request, 'Review updated successfully!')
            else:
                # Create new review
                new_review = Review.objects.create(
                    vendor=vendor,
                    supplier=supplier,
                    order=order,
                    rating=int(rating),
                    comment=comment,
                    title=f"Review for {supplier.business_name}",
                    is_verified_purchase=True if order else False
                )
                print(f"✅ Created new review ID: {new_review.id}")
                messages.success(request, 'Review submitted successfully!')
            
            print("="*50 + "\n")
            return redirect('leavereviews')
            
        except SupplierProfile.DoesNotExist:
            print(f"❌ Supplier with ID {supplier_id} not found")
            messages.error(request, 'Supplier not found')
            return redirect('leavereviews')
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error submitting review: {str(e)}')
            return redirect('leavereviews')

    return redirect('leavereviews')

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_vendor_orders(request):
    """Get orders for a vendor and supplier"""
    try:
        vendor = VendorProfile.objects.get(user=request.user)
    except VendorProfile.DoesNotExist:
        return Response({'error': 'Vendor profile not found'}, status=status.HTTP_403_FORBIDDEN)
    
    supplier_id = request.GET.get('supplier_id')
    
    if not supplier_id:
        return Response({'error': 'Supplier ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get ALL orders for this vendor-supplier pair
        orders = Order.objects.filter(
            vendor=request.user,
            supplier_id=supplier_id
        ).select_related('supplier_product__product').order_by('-created_at')
        
        print(f"\n🔍 Fetching orders for vendor {vendor.business_name}, supplier ID {supplier_id}")
        print(f"   Found {orders.count()} orders")
        
        # Check which orders already have reviews
        reviewed_order_ids = Review.objects.filter(
            vendor=vendor,
            supplier_id=supplier_id
        ).values_list('order_id', flat=True)
        
        order_data = []
        for order in orders:
            product_name = order.supplier_product.product.name if order.supplier_product and order.supplier_product.product else 'N/A'
            unit = order.supplier_product.product.unit if order.supplier_product and order.supplier_product.product else 'units'
            
            order_data.append({
                'id': order.id,
                'product_name': product_name,
                'quantity': float(order.quantity),
                'unit': unit,
                'total_price': float(order.total_price),
                'status': order.status,
                'created_at': order.created_at.strftime('%B %d, %Y'),
                'order_display': f"Order #{order.id} - {product_name} ({order.created_at.strftime('%b %d, %Y')}) - Status: {order.status.title()}",
                'has_review': order.id in reviewed_order_ids
            })
            print(f"   - Order #{order.id}: {product_name}, Status: {order.status}")
        
        return Response({
            'success': True,
            'orders': order_data
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========== API VIEWS ==========

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
        if not hasattr(self.request.user, 'vendor_profile'):
            raise permissions.PermissionDenied("Only vendors can create reviews")
        
        serializer.save(vendor=self.request.user.vendor_profile)


class ReviewUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewUpdateSerializer
    
    def get_queryset(self):
        return Review.objects.filter(vendor__user=self.request.user)


class ReviewDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
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
        if not hasattr(self.request.user, 'vendor_profile'):
            raise permissions.PermissionDenied("Only vendors can create product reviews")
        
        serializer.save(vendor=self.request.user.vendor_profile)


class ProductReviewUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductReviewUpdateSerializer
    
    def get_queryset(self):
        return ProductReview.objects.filter(vendor__user=self.request.user)


class ProductReviewDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
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
        
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[i] = reviews.filter(rating=i).count()
        
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