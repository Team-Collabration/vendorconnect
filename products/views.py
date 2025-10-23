from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count, Min, Max
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, IntegrityError
import json
import logging

from .serializers import (
    CategorySerializer, ProductSerializer, SupplierProductSerializer,
    SupplierProductCreateSerializer, ProductSearchSerializer,
    SupplierProductUpdateSerializer
)
from .models import Category, Product, SupplierProduct
from orders.models import SupplierProfile  # Import from orders app
# Set up logging
logger = logging.getLogger(__name__)


# ==================== Error Handler Decorator ====================
def handle_api_errors(view_func):
    """Decorator for consistent error handling across views"""
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ObjectDoesNotExist as e:
            logger.error(f"Object not found: {str(e)}")
            return Response(
                {'error': 'Resource not found', 'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {'error': 'Validation failed', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            return Response(
                {'error': 'Data integrity violation', 'detail': 'This operation conflicts with existing data'},
                status=status.HTTP_409_CONFLICT
            )
        except DatabaseError as e:
            logger.critical(f"Database error: {str(e)}")
            return Response(
                {'error': 'Database error', 'detail': 'An error occurred while accessing the database'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Internal server error', 'detail': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper


# ==================== DEBUG: Check Database ====================
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def debug_data(request):
    """Debug endpoint to check database content"""
    try:
        total_supplier_products = SupplierProduct.objects.count()
        available_supplier_products = SupplierProduct.objects.filter(is_available=True).count()
        total_products = Product.objects.count()
        total_suppliers = SupplierProfile.objects.count()
        total_categories = Category.objects.count()
        
        # Get sample data
        sample_products = SupplierProduct.objects.filter(is_available=True).select_related(
            'product', 'supplier', 'supplier__user'
        )[:5]
        
        sample_data = []
        for sp in sample_products:
            sample_data.append({
                'id': sp.id,
                'product_name': sp.product.name,
                'supplier_name': sp.supplier.business_name,
                'price': float(sp.price),
                'is_available': sp.is_available,
                'has_lat': hasattr(sp.supplier.user, 'latitude') and sp.supplier.user.latitude is not None,
                'has_lng': hasattr(sp.supplier.user, 'longitude') and sp.supplier.user.longitude is not None,
            })
        
        return Response({
            'total_supplier_products': total_supplier_products,
            'available_supplier_products': available_supplier_products,
            'total_products': total_products,
            'total_suppliers': total_suppliers,
            'total_categories': total_categories,
            'sample_products': sample_data,
            'message': 'If available_supplier_products is 0, you need to add products first'
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Error checking database'
        }, status=500)


# Add this import at the top
from django.contrib.auth.decorators import login_required

# Add this new view function
@login_required
def compareprices(request):
    """Render compare prices page with grouped product data"""
    try:
        # Get all available supplier products with related data
        supplier_products = SupplierProduct.objects.filter(
            is_available=True
        ).select_related(
            'product', 'product__category', 'supplier', 'supplier__user'
        ).order_by('product__name', 'price')

        # Group products by product name
        grouped = {}
        for sp in supplier_products:
            product_name = sp.product.name
            
            if product_name not in grouped:
                grouped[product_name] = []
            
            # Get supplier location
            lat = getattr(sp.supplier.user, 'latitude', None)
            lng = getattr(sp.supplier.user, 'longitude', None)
            
            grouped[product_name].append({
                'name': sp.supplier.business_name,
                'supplier_id': sp.supplier.id,
                'product_id': sp.id,
                'price': float(sp.price),
                'unit': sp.product.unit,
                'stock': float(sp.stock_quantity),  # Add this
                'minimum_order': float(sp.minimum_order_quantity),  # Add this
                'lat': float(lat) if lat is not None else 0.0,
                'lng': float(lng) if lng is not None else 0.0,
                'phone': sp.supplier.phone or 'N/A',
            })

        print(f"DEBUG: Total products grouped: {len(grouped)}")
        for product_name, suppliers in grouped.items():
            print(f"  - {product_name}: {len(suppliers)} suppliers, prices: {[s['price'] for s in suppliers]}")

        context = {'grouped': grouped}
        return render(request, 'compareprices.html', context)
        
    except Exception as e:
        logger.error(f"Error in compareprices view: {str(e)}", exc_info=True)
        return render(request, 'compareprices.html', {'grouped': {}})
    
    
    
# ==================== API Version of Compare Prices ====================
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def compare_prices_api(request):
    """API endpoint to get grouped products for price comparison"""
    try:
        supplier_products = SupplierProduct.objects.filter(
            is_available=True
        ).select_related(
            'product', 'product__category', 'supplier', 'supplier__user'
        ).order_by('product__name', 'price')

        # Group products by product name
        grouped = {}
        for sp in supplier_products:
            product_name = sp.product.name
            
            if product_name not in grouped:
                grouped[product_name] = []
            
            lat = getattr(sp.supplier.user, 'latitude', None)
            lng = getattr(sp.supplier.user, 'longitude', None)
            
            grouped[product_name].append({
                'name': sp.supplier.business_name,
                'price': float(sp.price),
                'stock': float(sp.stock_quantity),
                'lat': float(lat) if lat is not None else 0.0,
                'lng': float(lng) if lng is not None else 0.0,
                'supplier_id': sp.supplier.id,
                'product_id': sp.id
            })

        return Response({
            'success': True,
            'total_products': len(grouped),
            'grouped': grouped
        })
        
    except Exception as e:
        logger.error(f"Error in compare_prices_api: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e),
            'grouped': {}
        }, status=500)


# ==================== Category Views ====================
class CategoryListView(generics.ListAPIView):
    """Get all categories"""
    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    @handle_api_errors
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CategoryDetailView(generics.RetrieveAPIView):
    """Get single category details"""
    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    @handle_api_errors
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


# ==================== Product Views ====================
class ProductListView(generics.ListAPIView):
    """Get all active products"""
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    @handle_api_errors
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveAPIView):
    """Get single product details"""
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_active=True)

    @handle_api_errors
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


# ==================== Supplier Product Views ====================
class SupplierProductListView(generics.ListAPIView):
    """Get all available supplier products with filters"""
    permission_classes = [permissions.AllowAny]
    serializer_class = SupplierProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'product__category', 'is_available']
    search_fields = ['product__name', 'description']
    ordering_fields = ['price', 'created_at']
    
    def get_queryset(self):
        try:
            queryset = SupplierProduct.objects.filter(is_available=True)
        
            # Filter by supplier_id
            supplier_id = self.request.query_params.get('supplier_id')
            if supplier_id:
                try:
                    queryset = queryset.filter(supplier__id=supplier_id)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid supplier_id: {supplier_id}")
        
            # Filter by price range
            min_price = self.request.query_params.get('min_price')
            max_price = self.request.query_params.get('max_price')
        
            if min_price:
                try:
                    queryset = queryset.filter(price__gte=float(min_price))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid min_price: {min_price}")
                    
            if max_price:
                try:
                    queryset = queryset.filter(price__lte=float(max_price))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid max_price: {max_price}")
        
            # Filter by supplier location
            lat = self.request.query_params.get('lat')
            lng = self.request.query_params.get('lng')
        
            if lat and lng:
                queryset = queryset.filter(
                    Q(supplier__user__latitude__isnull=False) &
                    Q(supplier__user__longitude__isnull=False)
                )    
        
            return queryset
        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}")
            return SupplierProduct.objects.none()

    @handle_api_errors
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class SupplierProductDetailView(generics.RetrieveAPIView):
    """Get single supplier product details"""
    permission_classes = [permissions.AllowAny]
    serializer_class = SupplierProductSerializer
    queryset = SupplierProduct.objects.all()

    @handle_api_errors
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class SupplierProductCreateView(APIView):
    """Create a new supplier product"""
    permission_classes = [permissions.IsAuthenticated]

    @handle_api_errors
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        
        product_name = data.get("product_name", "").strip()
        category_name = data.get("category_name", "").strip()
        price = data.get("price")
        stock_quantity = data.get("stock_quantity", 0)
        minimum_order_quantity = data.get("minimum_order_quantity", 1)
        is_available = data.get("is_available", True)

        # Validate required fields
        if not product_name or not category_name or not price:
            return Response(
                {"error": "Missing required fields", "required": ["product_name", "category_name", "price"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate price and quantity
        try:
            price = float(price)
            stock_quantity = float(stock_quantity)
            minimum_order_quantity = float(minimum_order_quantity)
            
            if price <= 0:
                return Response(
                    {"error": "Validation failed", "detail": "Price must be greater than 0"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if stock_quantity < 0:
                return Response(
                    {"error": "Validation failed", "detail": "Stock quantity cannot be negative"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if minimum_order_quantity <= 0:
                return Response(
                    {"error": "Validation failed", "detail": "Minimum order quantity must be greater than 0"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError) as e:
            return Response(
                {"error": "Invalid input", "detail": "Price and quantity values must be valid numbers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create category
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={"description": f"{category_name} products"}
        )

        # Get or create product
        product, created = Product.objects.get_or_create(
            name=product_name,
            category=category,
            defaults={
                "unit": "kg",
                "is_active": True,
                "description": f"{product_name} from {category_name} category"
            }
        )

        # Get or create supplier profile
        supplier_profile, created = SupplierProfile.objects.get_or_create(
            user=user,
            defaults={
                'business_name': f"{user.username}'s Business",
                'phone': '0000000000'
            }
        )

        # Check if supplier already has this product
        if SupplierProduct.objects.filter(supplier=supplier_profile, product=product).exists():
            return Response(
                {"error": "Duplicate product", "detail": f"{product_name} already exists in your product list"},
                status=status.HTTP_409_CONFLICT
            )

        # Create SupplierProduct
        supplier_product = SupplierProduct.objects.create(
            supplier=supplier_profile,
            product=product,
            price=price,
            stock_quantity=stock_quantity,
            minimum_order_quantity=minimum_order_quantity,
            is_available=is_available
        )

        return Response(
            {
                "success": True,
                "message": "Product created successfully",
                "data": SupplierProductSerializer(supplier_product).data
            },
            status=status.HTTP_201_CREATED
        )


class SupplierProductUpdateView(generics.UpdateAPIView):
    """Update supplier product (only own products)"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SupplierProductUpdateSerializer
    
    def get_queryset(self):
        try:
            supplier_profile, created = SupplierProfile.objects.get_or_create(
                user=self.request.user,
                defaults={'business_name': f"{self.request.user.username}'s Business"}
            )
            return SupplierProduct.objects.filter(supplier=supplier_profile)
        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}")
            return SupplierProduct.objects.none()

    @handle_api_errors
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class SupplierProductDeleteView(generics.DestroyAPIView):
    """Delete supplier product (only own products)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            supplier_profile, created = SupplierProfile.objects.get_or_create(
                user=self.request.user,
                defaults={'business_name': f"{self.request.user.username}'s Business"}
            )
            return SupplierProduct.objects.filter(supplier=supplier_profile)
        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}")
            return SupplierProduct.objects.none()
    
    @handle_api_errors
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product_name = instance.product.name
        self.perform_destroy(instance)
        return Response(
            {"success": True, "message": f"Product '{product_name}' deleted successfully"},
            status=status.HTTP_200_OK
        )


# ==================== Search & Filter Views ====================
class ProductSearchView(APIView):
    """Advanced product search with multiple filters"""
    permission_classes = [permissions.AllowAny]
    
    @handle_api_errors
    def post(self, request):
        serializer = ProductSearchSerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data.get('query', '')
            category = serializer.validated_data.get('category')
            min_price = serializer.validated_data.get('min_price')
            max_price = serializer.validated_data.get('max_price')
            supplier_id = serializer.validated_data.get('supplier_id')
            
            queryset = SupplierProduct.objects.filter(is_available=True)
            
            # Apply filters
            if query:
                queryset = queryset.filter(
                    Q(product__name__icontains=query) |
                    Q(description__icontains=query)
                )
            
            if category:
                queryset = queryset.filter(product__category_id=category)
            
            if min_price:
                queryset = queryset.filter(price__gte=min_price)
            
            if max_price:
                queryset = queryset.filter(price__lte=max_price)
            
            if supplier_id:
                queryset = queryset.filter(supplier_id=supplier_id)
            
            # Order by price
            queryset = queryset.order_by('price')
            
            serializer = SupplierProductSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data})
        
        return Response(
            {"error": "Validation failed", "detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class SupplierProductsView(generics.ListAPIView):
    """Get all products from a specific supplier"""
    permission_classes = [permissions.AllowAny]
    serializer_class = SupplierProductSerializer
    
    def get_queryset(self):
        supplier_id = self.kwargs.get('supplier_id')
        try:
            return SupplierProduct.objects.filter(
                supplier_id=supplier_id,
                is_available=True
            )
        except Exception as e:
            logger.error(f"Error getting supplier products: {str(e)}")
            return SupplierProduct.objects.none()

    @handle_api_errors
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class MySupplierProductsView(generics.ListAPIView):
    """Get logged-in supplier's own products"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SupplierProductSerializer
    
    def get_queryset(self):
        try:
            supplier_profile, created = SupplierProfile.objects.get_or_create(
                user=self.request.user,
                defaults={'business_name': f"{self.request.user.username}'s Business"}
            )
            return SupplierProduct.objects.filter(supplier=supplier_profile).order_by('-created_at')
        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}")
            return SupplierProduct.objects.none()

    @handle_api_errors
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# ==================== Analytics & Summary Views ====================
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@handle_api_errors
def product_categories(request):
    """Get all product categories with product counts"""
    categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    )
    serializer = CategorySerializer(categories, many=True)
    return Response({"success": True, "data": serializer.data})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@handle_api_errors
def supplier_products_summary(request, supplier_id):
    """Get summary of supplier's products"""
    try:
        supplier = SupplierProfile.objects.get(id=supplier_id)
    except SupplierProfile.DoesNotExist:
        return Response(
            {'error': 'Supplier not found', 'detail': f'No supplier exists with ID: {supplier_id}'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    products = SupplierProduct.objects.filter(
        supplier=supplier, 
        is_available=True
    )
    
    # Calculate price statistics
    price_stats = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price'),
        avg_price=Avg('price')
    )
    
    summary = {
        'success': True,
        'supplier_id': supplier.id,
        'supplier_name': supplier.business_name,
        'total_products': products.count(),
        'categories': products.values('product__category__name').distinct().count(),
        'price_range': {
            'min': float(price_stats['min_price']) if price_stats['min_price'] else 0,
            'max': float(price_stats['max_price']) if price_stats['max_price'] else 0,
            'avg': float(price_stats['avg_price']) if price_stats['avg_price'] else 0
        }
    }
    
    return Response(summary)


# ==================== Location Views ====================
@login_required
@csrf_exempt
def save_location(request):
    """Save supplier's location"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False, 
            'error': 'Invalid request method. Only POST is allowed'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        lat = data.get('lat')
        lng = data.get('lng')
        
        if not lat or not lng:
            return JsonResponse({
                'success': False, 
                'error': 'Missing required fields: lat and lng'
            }, status=400)
        
        # Validate coordinates
        try:
            lat = float(lat)
            lng = float(lng)
            
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return JsonResponse({
                    'success': False, 
                    'error': 'Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False, 
                'error': 'Coordinates must be valid numbers'
            }, status=400)
        
        # Get or create supplier profile
        supplier, created = SupplierProfile.objects.get_or_create(
            user=request.user,
            defaults={'business_name': f"{request.user.username}'s Business"}
        )
        
        # Store in User model
        request.user.latitude = lat
        request.user.longitude = lng
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Location saved successfully'
        })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error saving location: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False, 
            'error': 'An error occurred while saving location'
        }, status=500)


@login_required
def get_location(request):
    """Get supplier's location"""
    try:
        if hasattr(request.user, 'latitude') and hasattr(request.user, 'longitude'):
            if request.user.latitude is not None and request.user.longitude is not None:
                return JsonResponse({
                    'success': True,
                    'latitude': float(request.user.latitude),
                    'longitude': float(request.user.longitude)
                })
        
        return JsonResponse({
            'success': False,
            'error': 'Location not set'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Error getting location: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while retrieving location'
        }, status=500)
        
        
