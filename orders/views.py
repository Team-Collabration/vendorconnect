# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from venv import logger
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Supplier, SupplierProfile  # import the correct model
import math
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# ✅ Keep this fully unindented
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_supplier_products(request):
    """Get all available supplier products for bulk ordering"""
    try:
        products = SupplierProduct.objects.filter(
            is_available=True,
            stock_quantity__gt=0
        ).select_related(
            'supplier', 'supplier__user', 'product'
        ).order_by('-created_at')
        
        products_data = []
        for sp in products:
            products_data.append({
                'id': sp.id,
                'product_name': sp.product.name,
                'supplier_name': sp.supplier.business_name,
                'supplier_phone': sp.supplier.phone or 'N/A',
                'price': float(sp.price),
                'unit': sp.product.unit,
                'stock_quantity': float(sp.stock_quantity),
                'minimum_order_quantity': float(sp.minimum_order_quantity),
                'description': sp.description or ''
            })
        
        return Response({
            'success': True,
            'products': products_data,
            'total': len(products_data)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

# Helper function
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

@api_view(['GET'])
def nearby_suppliers(request):
    """Get nearby suppliers based on location"""
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    item = request.GET.get('item', None)
    
    if not lat or not lng:
        return Response({'success': False, 'error': 'Latitude and longitude are required'}, status=400)
    
    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return Response({'success': False, 'error': 'Invalid coordinates'}, status=400)
    
    # Use SupplierProfile if that stores user location
    suppliers = SupplierProfile.objects.select_related('user').filter(
        user__latitude__isnull=False,
        user__longitude__isnull=False
    )
    
    supplier_list = []
    for supplier in suppliers:
        supplier_lat = float(supplier.user.latitude)
        supplier_lng = float(supplier.user.longitude)
        distance = haversine_distance(lat, lng, supplier_lat, supplier_lng)
        
        supplier_data = {
            'user_id': supplier.user.id,
            'supplier_id': supplier.id,
            'name': supplier.business_name,
            'username': supplier.user.username,
            'business_type': supplier.business_type or 'General',
            'phone': supplier.phone,
            'email': supplier.user.email,
            'lat': supplier_lat,
            'lng': supplier_lng,
            'distance': round(distance, 2)
        }
        supplier_list.append(supplier_data)
    
    supplier_list.sort(key=lambda x: x['distance'])
    
    return Response({'success': True, 'suppliers': supplier_list, 'total': len(supplier_list)})


@csrf_exempt
def save_supplier_location(request):
    if request.method == "POST":
        user = request.user
        try:
            data = json.loads(request.body)
            lat = data.get("lat")
            lng = data.get("lng")
        except:
            return JsonResponse({"success": False, "error": "Invalid data"})

        try:
            supplier = Supplier.objects.get(user=user)
            supplier.lat = lat
            supplier.lng = lng
            supplier.save()
            return JsonResponse({"success": True})
        except Supplier.DoesNotExist:
            return JsonResponse({"success": False, "error": "Supplier not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})


# orders/views.py - ADD THIS NEW VIEW
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import SupplierProduct

@login_required
def create_quick_order(request, supplier_product_id):
    """Create order directly from compare prices page"""
    if request.method == 'POST':
        try:
            supplier_product = SupplierProduct.objects.select_related(
                'supplier', 'product'
            ).get(id=supplier_product_id)
            
            # Get or create vendor profile
            from orders.models import VendorProfile
            vendor_profile, _ = VendorProfile.objects.get_or_create(
                user=request.user,
                defaults={'business_name': f"{request.user.username}'s Business"}
            )
            
            # Redirect to order creation page with pre-filled data
            # Or create the order directly here
            messages.success(
                request, 
                f"Order placed for {supplier_product.product.name} from {supplier_product.supplier.business_name}"
            )
            return redirect('compareprices')
            
        except SupplierProduct.DoesNotExist:
            messages.error(request, "Product not found")
            return redirect('compareprices')
        except Exception as e:
            messages.error(request, f"Error placing order: {str(e)}")
            return redirect('compareprices')
    
    return redirect('compareprices')


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from products.models import SupplierProduct
from .models import Order, SupplierProfile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create a new order from vendor to supplier"""
    try:
        supplier_product_id = request.data.get('supplier_product_id')
        quantity = request.data.get('quantity')
        delivery_address = request.data.get('delivery_address')
        phone = request.data.get('phone')
        expected_delivery_date = request.data.get('expected_delivery_date')
        notes = request.data.get('notes', '')
        
        print(f"DEBUG: Order request - Product ID: {supplier_product_id}, Quantity: {quantity}")
        
        if not supplier_product_id or not quantity:
            return Response({
                'success': False,
                'error': 'Product and quantity are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not delivery_address or not phone:
            return Response({
                'success': False,
                'error': 'Delivery address and phone number are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get supplier product
        try:
            supplier_product = SupplierProduct.objects.select_related(
                'supplier', 'supplier__user', 'product'
            ).get(id=supplier_product_id, is_available=True)
            
            print(f"DEBUG: Found product: {supplier_product.product.name} from {supplier_product.supplier.business_name}")
        except SupplierProduct.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Product not found or not available'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validate quantity
        try:
            quantity = Decimal(quantity)
            if quantity < supplier_product.minimum_order_quantity:
                return Response({
                    'success': False,
                    'error': f'Minimum order quantity is {supplier_product.minimum_order_quantity} {supplier_product.product.unit}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if quantity > supplier_product.stock_quantity:
                return Response({
                    'success': False,
                    'error': f'Insufficient stock. Available: {supplier_product.stock_quantity} {supplier_product.product.unit}'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'Invalid quantity'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total price
        unit_price = supplier_product.price
        total_price = unit_price * quantity
        
        # Create order with all details
        order = Order.objects.create(
            vendor=request.user,
            supplier=supplier_product.supplier,
            supplier_product=supplier_product,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            delivery_address=delivery_address,
            phone=phone,
            expected_delivery_date=expected_delivery_date if expected_delivery_date else None,
            notes=notes,
            status='pending'
        )
        # Reduce stock
        supplier_product.stock_quantity -= quantity
        if supplier_product.stock_quantity == 0:
            supplier_product.is_available = False
        supplier_product.save()
                # -------------------------
        # Send notification to supplier
        # -------------------------
        from .models import Notification  # Make sure Notification is imported at the top

        Notification.objects.create(
            user=order.supplier.user,  # the supplier's user account
            order=order,
            title="New Order Received",
            message=f"You have received a new order for {supplier_product.product.name} from {request.user.username}",
            notification_type="new_order"
        )

        print(f"DEBUG: Order created successfully - Order ID: {order.id}")
        
        # TODO: Send notification to supplier (email/SMS)
        
        return Response({
            'success': True,
            'message': 'Order placed successfully',
            'order': {
                'id': order.id,
                'product_name': supplier_product.product.name,
                'supplier_name': supplier_product.supplier.business_name,
                'quantity': float(quantity),
                'unit': supplier_product.product.unit,
                'unit_price': float(unit_price),
                'total_price': float(total_price),
                'status': order.status,
                'created_at': order.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)

        print(f"DEBUG: Order created successfully - Order ID: {order.id}")

        # TODO: Send notification to supplier (email/SMS)

        print(f"DEBUG: Notification sent to supplier - Order ID: {order.id}")
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': f'Failed to create order: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # API to get supplier's received orders

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_orders(request):
    """Get all orders received by the supplier"""
    try:
        # Get supplier profile
        supplier_profile = SupplierProfile.objects.get(user=request.user)
        
        print(f"DEBUG: Fetching orders for supplier: {supplier_profile.business_name}")
        
        # Get all orders for this supplier
        orders = Order.objects.filter(
            supplier=supplier_profile
        ).select_related(
            'vendor', 'supplier_product', 'supplier_product__product'
        ).order_by('-created_at')
        
        print(f"DEBUG: Found {orders.count()} orders for supplier")
        
        orders_data = []
        for order in orders:
            order_dict = {
                'id': order.id,
                'vendor_name': order.vendor.username,
                'vendor_email': order.vendor.email,
                'product_name': order.supplier_product.product.name,
                'quantity': float(order.quantity),
                'unit': order.supplier_product.product.unit,
                'unit_price': float(order.unit_price),
                'total_price': float(order.total_price),
                'status': order.status,
                'delivery_address': order.delivery_address or 'N/A',
                'phone': order.phone or 'N/A',
                'expected_delivery_date': order.expected_delivery_date.isoformat() if order.expected_delivery_date else None,
                'notes': order.notes or '',
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            }
            orders_data.append(order_dict)
            print(f"DEBUG: Order #{order.id} - {order.vendor.username} - {order.supplier_product.product.name}")
        
        return Response({
            'success': True,
            'orders': orders_data,
            'total': len(orders_data)
        })
        
    except SupplierProfile.DoesNotExist:
        print(f"DEBUG: Supplier profile not found for user: {request.user.username}")
        return Response({
            'success': False,
            'error': 'Supplier profile not found'
        }, status=404)
    except Exception as e:
        print(f"ERROR fetching supplier orders: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# API to update order status (supplier only)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status by supplier"""
    try:
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({
                'success': False,
                'error': 'Status is required'
            }, status=400)
        
        # Validate status
        valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return Response({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }, status=400)
        
        # Get supplier profile
        supplier_profile = SupplierProfile.objects.get(user=request.user)
        
        # Get order and verify it belongs to this supplier
        order = Order.objects.get(id=order_id, supplier=supplier_profile)
        
        # Update status
        old_status = order.status
        order.status = new_status
        order.save()
        #_______________________
        # Send notification to vendor about status change
        Notification.objects.create(
    user=order.vendor,
    order=order,
    title=f"Order {new_status.title()}",
    message=f"Your order for {order.supplier_product.product.name} has been {new_status} by {request.user.username}",
    notification_type=f"order_{new_status}"
)
        logger.info(f"Order #{order.id} status changed from {old_status} to {new_status}")
        

    
        return Response({
            'success': True,
            'message': f'Order status updated to {new_status}',
            'order': {
                'id': order.id,
                'status': order.status,
                'updated_at': order.updated_at.isoformat()
            }
        })
        
    except SupplierProfile.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Supplier profile not found'
        }, status=404)
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Order not found or you do not have permission to update it'
        }, status=404)
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_orders(request):
    """Get all orders placed by the vendor"""
    try:
        print(f"DEBUG: Fetching orders for vendor: {request.user.username}")
        
        # Get all orders placed by this vendor
        orders = Order.objects.filter(
            vendor=request.user
        ).select_related(
            'supplier', 'supplier_product', 'supplier_product__product'
        ).order_by('-created_at')
        
        print(f"DEBUG: Found {orders.count()} orders for vendor")
        
        orders_data = []
        for order in orders:
            order_dict = {
                'id': order.id,
                'supplier_name': order.supplier.business_name,
                'supplier_phone': order.supplier.phone or 'N/A',
                'product_name': order.supplier_product.product.name,
                'quantity': float(order.quantity),
                'unit': order.supplier_product.product.unit,
                'unit_price': float(order.unit_price),
                'total_price': float(order.total_price),
                'status': order.status,
                'status_display': order.status.title(),
                'delivery_address': order.delivery_address or 'N/A',
                'phone': order.phone or 'N/A',
                'expected_delivery_date': order.expected_delivery_date.isoformat() if order.expected_delivery_date else None,
                'notes': order.notes or '',
                'delivery_address': order.delivery_address or 'N/A',
                'phone': order.phone or 'N/A',
                'expected_delivery_date': order.expected_delivery_date.isoformat() if order.expected_delivery_date else None,

                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            }
            orders_data.append(order_dict)
            print(f"DEBUG: Order #{order.id} - {order.supplier.business_name} - {order.supplier_product.product.name}")
        
        return Response({
            'success': True,
            'orders': orders_data,
            'total': len(orders_data)
        })
        
    except Exception as e:
        print(f"ERROR fetching vendor orders: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
    return render(request, 'orders.html')

# Template views
@login_required
def manageorders_template(request):
    """Render manage orders page for supplier"""
    return render(request, 'manageorders.html')


# Add these imports at the top of views.py
from django.db.models import Sum, Count, Avg, Q
from datetime import datetime, timedelta
from decimal import Decimal

# Add this view function to views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_analytics(request):
    """Get analytics data for supplier dashboard"""
    try:
        # Get supplier profile
        supplier_profile = SupplierProfile.objects.get(user=request.user)
        
        # Get all orders for this supplier
        orders = Order.objects.filter(supplier=supplier_profile)
        
        # Basic metrics
        total_orders = orders.count()
        completed_orders = orders.filter(status='delivered').count()
        pending_orders = orders.filter(status__in=['pending', 'confirmed']).count()
        
        # Revenue calculation (only from delivered orders)
        total_revenue = orders.filter(status='delivered').aggregate(
            total=Sum('total_price')
        )['total'] or Decimal('0')
        
        # Average order value
        avg_order_value = orders.filter(status='delivered').aggregate(
            avg=Avg('total_price')
        )['avg'] or Decimal('0')
        
        # Unique vendors count
        unique_vendors = orders.values('vendor').distinct().count()
        
        # Last 7 days data
        today = datetime.now().date()
        last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        
        # Sales quantities for last 7 days
        last_7_days_quantities = []
        last_7_days_revenue = []
        last_7_days_labels = []
        
        for day in last_7_days:
            day_orders = orders.filter(
                created_at__date=day,
                status='delivered'
            )
            
            quantity = day_orders.aggregate(total=Sum('quantity'))['total'] or 0
            revenue = day_orders.aggregate(total=Sum('total_price'))['total'] or Decimal('0')
            
            last_7_days_quantities.append(float(quantity))
            last_7_days_revenue.append(float(revenue))
            last_7_days_labels.append(day.strftime('%b %d'))
        
        # Order status distribution
        status_distribution = []
        for status_code, status_name in Order.STATUS_CHOICES:
            count = orders.filter(status=status_code).count()
            if count > 0:
                status_distribution.append({
                    'status': status_code,
                    'count': count
                })
        
        # Top 5 products by quantity sold
        from django.db.models import F
        top_products = orders.values(
            'supplier_product__product__name',
            'supplier_product__product__unit'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price'),
            order_count=Count('id')
        ).order_by('-total_quantity')[:5]
        
        top_products_list = []
        for product in top_products:
            top_products_list.append({
                'product_name': product['supplier_product__product__name'],
                'unit': product['supplier_product__product__unit'],
                'total_quantity': float(product['total_quantity']),
                'total_revenue': float(product['total_revenue']),
                'order_count': product['order_count']
            })
        
        # Recent orders (last 10)
        recent_orders = orders.select_related(
            'vendor', 'supplier_product', 'supplier_product__product'
        ).order_by('-created_at')[:10]
        
        recent_orders_list = []
        for order in recent_orders:
            recent_orders_list.append({
                'id': order.id,
                'vendor_name': order.vendor.username,
                'product_name': order.supplier_product.product.name,
                'quantity': float(order.quantity),
                'unit': order.supplier_product.product.unit,
                'total_price': float(order.total_price),
                'status': order.status,
                'created_at': order.created_at.isoformat()
            })
        
        return Response({
            'success': True,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'total_revenue': float(total_revenue),
            'avg_order_value': float(avg_order_value),
            'unique_vendors': unique_vendors,
            'last_7_days_labels': last_7_days_labels,
            'last_7_days_quantities': last_7_days_quantities,
            'last_7_days_revenue': last_7_days_revenue,
            'status_distribution': status_distribution,
            'top_products': top_products_list,
            'recent_orders': recent_orders_list
        })
        
    except SupplierProfile.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Supplier profile not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error fetching supplier analytics: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def analytics_template(request):
    """Render analytics page for supplier"""
    return render(request, 'analytics.html')

## nnotifications##
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Notification
import json

@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """Get all notifications for the current user"""
    try:
        notifications = Notification.objects.filter(user=request.user).select_related('order')[:50]
        
        notifications_data = [{
            'id': notif.id,
            'notification_type': notif.notification_type,
            'title': notif.title,
            'message': notif.message,
            'order_id': notif.order.id if notif.order else None,
            'is_read': notif.is_read,
            'created_at': notif.created_at.isoformat()
        } for notif in notifications]
        
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_unread_count(request):
    """Get count of unread notifications"""
    try:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def mark_all_read(request):
    """Mark all notifications as read for the current user"""
    try:
        updated_count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'message': f'{updated_count} notifications marked as read'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    """Delete a single notification"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def clear_all_notifications(request):
    """Delete all notifications for the current user"""
    try:
        deleted_count, _ = Notification.objects.filter(user=request.user).delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} notifications cleared'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        # orders/views.py (or wherever order is created)
    