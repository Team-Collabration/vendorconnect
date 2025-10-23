# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import JsonResponse
import random
from datetime import datetime, timedelta

from orders.models import VendorProfile, SupplierProfile
from django.contrib.auth.decorators import login_required
from google.oauth2 import id_token
from google.auth.transport import requests

# ---------------------------
# Temporary OTP storage
# ---------------------------
otp_storage = {}        # email -> {'otp': code, 'timestamp': datetime}
verified_emails = set() # emails that verified OTP

# ---------------------------
# Get custom User model
# ---------------------------
User = get_user_model()


# ---------------------------
# SEND OTP
# ---------------------------
@csrf_exempt
def send_email_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            return JsonResponse({"status": "error", "message": "Email is required."}, status=400)

        otp = str(random.randint(100000, 999999))
        otp_storage[email] = {
            'otp': otp,
            'timestamp': datetime.now()
        }

        try:
            from django.conf import settings
            from django.core.mail import EmailMessage
            
            subject = "Your VendorConnect OTP"
            message = f"Your OTP for VendorConnect signup is {otp}. It is valid for 5 minutes."
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            
            email_message = EmailMessage(subject, message, email_from, recipient_list)
            email_message.send(fail_silently=False)
            
            # Print to console for development
            print(f"\n{'='*50}")
            print(f"OTP for {email}: {otp}")
            print(f"{'='*50}\n")
            
            return JsonResponse({
                "status": "success", 
                "message": f"OTP sent successfully to {email}"
            })
        except Exception as e:
            print(f"Email Error: {str(e)}")
            return JsonResponse({
                "status": "error", 
                "message": f"Failed to send OTP: {str(e)}"
            }, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)


# ---------------------------
# VERIFY OTP
# ---------------------------
@csrf_exempt
def verify_email_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        otp = request.POST.get("otp")

        if not email or not otp:
            return JsonResponse({"status": "error", "message": "Email and OTP are required."})

        if email not in otp_storage:
            return JsonResponse({"status": "error", "message": "No OTP sent to this email. Please request a new OTP."})

        stored_data = otp_storage[email]
        stored_otp = stored_data['otp']
        timestamp = stored_data['timestamp']

        # Check if OTP is expired (5 minutes)
        if datetime.now() - timestamp > timedelta(minutes=5):
            otp_storage.pop(email, None)
            return JsonResponse({"status": "error", "message": "OTP has expired. Please request a new one."})

        if stored_otp == otp:
            verified_emails.add(email)
            return JsonResponse({"status": "success", "message": "OTP verified successfully."})

        return JsonResponse({"status": "error", "message": "Invalid OTP. Please try again."})

    return JsonResponse({"status": "error", "message": "Invalid request."})


# ---------------------------
# VENDOR SIGNUP
# ---------------------------
def vendorsignup_template(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")
        dob = request.POST.get("dob")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")

        print(f"Vendor Signup attempt - Email: {email}, Username: {username}")

        # Check if email was verified
        if email not in verified_emails:
            messages.error(request, "Please verify your email with OTP first.")
            return redirect("vendorsignup")

        # Remove from verified emails after use
        verified_emails.discard(email)
        otp_storage.pop(email, None)

        # Password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("vendorsignup")

        # Unique username/email
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("vendorsignup")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("vendorsignup")

        # Create user WITH user_type
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type='vendor'  # ✅ CRITICAL
        )
        
        # Store phone number if provided
        if phone:
            user.phone_number = phone
        
        user.save()
        
        print(f"User created - ID: {user.id}, Type: {user.user_type}")

        # Create VendorProfile
        VendorProfile.objects.create(user=user, business_name=username)
        print(f"VendorProfile created for {username}")

        # Authenticate & login
        auth_user = authenticate(request, username=username, password=password)
        if auth_user:
            login(request, auth_user)
            messages.success(request, "Vendor signup successful!")
            return redirect("vendordashboard")
        else:
            messages.error(request, "Signup failed. Please try logging in.")
            return redirect("vendorsignup")

    return render(request, "vendorsignup.html")


# ---------------------------
# SUPPLIER SIGNUP
# ---------------------------
def supplier_signup_template(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")
        dob = request.POST.get("dob")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")

        print(f"Supplier Signup attempt - Email: {email}, Username: {username}")

        # Check if email was verified
        if email not in verified_emails:
            messages.error(request, "Please verify your email with OTP first.")
            return redirect("suppliersignup")

        # Remove from verified emails after use
        verified_emails.discard(email)
        otp_storage.pop(email, None)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("suppliersignup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("suppliersignup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("suppliersignup")

        # Create user WITH user_type
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type='supplier'  # ✅ CRITICAL
        )
        
        # Store phone number if provided
        if phone:
            user.phone_number = phone
        
        user.save()
        
        print(f"User created - ID: {user.id}, Type: {user.user_type}")
        
        # Create SupplierProfile
        SupplierProfile.objects.create(user=user, business_name=username)
        print(f"SupplierProfile created for {username}")

        auth_user = authenticate(request, username=username, password=password)
        if auth_user:
            login(request, auth_user)
            messages.success(request, "Signup successful!")
            return redirect("suppliers-dashboard")
        else:
            messages.error(request, "Signup failed. Please try logging in.")
            return redirect("suppliersignup")

    return render(request, "suppliersignup.html")


# ---------------------------
# VENDOR LOGIN
# ---------------------------
def vendor_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(f"Vendor Login attempt - Email: {email}")
        
        try:
            user = User.objects.get(email=email)
            print(f"User found - Username: {user.username}, Type: {user.user_type}")
            
            # Check if user is a vendor
            if user.user_type != "vendor":
                messages.error(request, "This account is not registered as a vendor.")
                return redirect("vendorlogin")
                
        except User.DoesNotExist:
            print(f"No user found with email: {email}")
            messages.error(request, "No account found with that email.")
            return redirect("vendorlogin")

        auth_user = authenticate(request, username=user.username, password=password)
        if auth_user:
            login(request, auth_user)
            print(f"Login successful for {user.username}")
            messages.success(request, "Login successful!")
            return redirect("vendordashboard")
        else:
            print(f"Authentication failed for {user.username}")
            messages.error(request, "Invalid password.")
            return redirect("vendorlogin")

    return render(request, "vendorlogin.html")


# ---------------------------
# SUPPLIER LOGIN
# ---------------------------
@csrf_exempt
def supplier_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(f"Supplier Login attempt - Email: {email}")
        
        try:
            user = User.objects.get(email=email)
            print(f"User found - Username: {user.username}, Type: {user.user_type}")
            
            # Check if user is a supplier
            if user.user_type != "supplier":
                messages.error(request, "This account is not registered as a supplier.")
                return redirect("supplierlogin")
                
        except User.DoesNotExist:
            print(f"No user found with email: {email}")
            messages.error(request, "No account found with that email.")
            return redirect("supplierlogin")

        auth_user = authenticate(request, username=user.username, password=password)
        if auth_user:
            login(request, auth_user)
            print(f"Login successful for {user.username}")
            messages.success(request, "Login successful!")
            return redirect("suppliers-dashboard")
        else:
            print(f"Authentication failed for {user.username}")
            messages.error(request, "Invalid password.")
            return redirect("supplierlogin")

    return render(request, "supplierlogin.html")


# ---------------------------
# GOOGLE SIGNUP
# ---------------------------
@csrf_exempt
def google_signup(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "error": "Invalid request method"}, status=400)

    token = request.POST.get("credential")
    account_type = request.POST.get("account_type")

    if not token or not account_type:
        return JsonResponse({"status": "error", "error": "Missing credentials"}, status=400)

    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(),
            "1013464190681-ptkqjpjqh7v440t5fnv5aou116fmtb80.apps.googleusercontent.com"
        )
        email = idinfo["email"]
        name = idinfo.get("name", "")
        first_name = name.split(" ")[0] if " " in name else name
        last_name = name.split(" ")[1] if " " in name else ""

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": first_name,
                "last_name": last_name,
                "user_type": account_type,
            }
        )

        if created:
            if account_type == "vendor":
                VendorProfile.objects.create(user=user, business_name=first_name)
            elif account_type == "supplier":
                SupplierProfile.objects.create(user=user, business_name=first_name)

        login(request, user)
        redirect_url = "/vendors/dashboard/" if account_type == "vendor" else "/suppliers/dashboard/"
        return JsonResponse({"status": "success", "redirect_url": redirect_url})

    except ValueError:
        return JsonResponse({"status": "error", "error": "Invalid Google token"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)}, status=500)


@login_required
def google_redirect(request):
    user = request.user
    if hasattr(user, 'vendor_profile'):
        return redirect('vendordashboard')
    elif hasattr(user, 'supplier_profile'):
        return redirect('suppliers-dashboard')
    else:
        return redirect('index')


# ---------------------------
# VIEW PROFILE
# ---------------------------
@login_required
def view_profile(request):
    user = request.user
    try:
        profile = SupplierProfile.objects.get(user=user)
    except SupplierProfile.DoesNotExist:
        profile = None

    context = {
        'user': user,
        'profile': profile
    }
    return render(request, 'view_profile.html', context)


# ---------------------------
# EDIT PROFILE
# ---------------------------
@login_required
def edit_profile(request):
    user = request.user
    try:
        profile = SupplierProfile.objects.get(user=user)
    except SupplierProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        user.save()

        business_name = request.POST.get('business_name', '')
        business_type = request.POST.get('business_type', '')
        gst_number = request.POST.get('gst_number', '')
        pan_number = request.POST.get('pan_number', '')

        if profile:
            profile.business_name = business_name
            profile.business_type = business_type
            profile.gst_number = gst_number
            profile.pan_number = pan_number
            profile.save()
        else:
            profile = SupplierProfile.objects.create(
                user=user,
                business_name=business_name,
                business_type=business_type,
                gst_number=gst_number,
                pan_number=pan_number
            )

        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password and new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
        elif new_password:
            messages.error(request, "Passwords do not match!")

        messages.success(request, "Profile updated successfully!")
        return redirect('view_profile')

    context = {
        'user': user,
        'profile': profile
    }
    return render(request, 'edit_profile.html', context)


# ---------------------------
# LOGOUT
# ---------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("index")


# ---------------------------
# DASHBOARDS
# ---------------------------
def supplier_dashboard_template(request):
    return render(request, "suppliers-dashboard.html")


def vendor_dashboard_template(request):
    return render(request, "vendordashboard.html")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from math import radians, sin, cos, sqrt, atan2

# Save supplier location
@login_required
@csrf_exempt
def save_supplier_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = data.get('lat')
            lng = data.get('lng')
            
            if lat and lng:
                user = request.user
                user.latitude = lat
                user.longitude = lng
                user.save()
                
                print(f"✅ Location saved for {user.username}: {lat}, {lng}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Location saved successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid coordinates'
                }, status=400)
                
        except Exception as e:
            print(f"❌ Error saving location: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


# Get supplier's saved location
@login_required
def get_supplier_location(request):
    try:
        user = request.user
        if user.latitude and user.longitude:
            return JsonResponse({
                'success': True,
                'latitude': float(user.latitude),
                'longitude': float(user.longitude)
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No location saved'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Calculate distance between two points (Haversine formula)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return round(distance, 2)


# API to get all suppliers with locations
@csrf_exempt
@csrf_exempt
def get_all_suppliers(request):
    try:
        # Get all suppliers who have saved their location
        suppliers = User.objects.filter(
            user_type='supplier',
            latitude__isnull=False,
            longitude__isnull=False
        ).select_related('supplier_profile')
        
        supplier_list = []
        for supplier in suppliers:
            # Skip if no supplier profile
            if not hasattr(supplier, 'supplier_profile'):
                continue
                
            supplier_data = {
                'id': supplier.id,
                'user_id': supplier.id,  # ✅ ADD THIS - User ID
                'supplier_id': supplier.supplier_profile.id,  # ✅ ADD THIS - SupplierProfile ID (CRITICAL)
                'name': supplier.supplier_profile.business_name,
                'lat': float(supplier.latitude),
                'lng': float(supplier.longitude),
                'email': supplier.email,
                'phone': supplier.phone_number or 'Not provided',
                'business_type': supplier.supplier_profile.business_type or 'General',
            }
            supplier_list.append(supplier_data)
        
        return JsonResponse({
            'success': True,
            'suppliers': supplier_list,
            'count': len(supplier_list)
        })
        
    except Exception as e:
        print(f"❌ Error fetching suppliers: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# API to get nearby suppliers for vendors
@csrf_exempt
def get_nearby_suppliers(request):
    try:
        vendor_lat = float(request.GET.get('lat'))
        vendor_lng = float(request.GET.get('lng'))
        search_item = request.GET.get('item', '').strip().lower()
        
        # Get all suppliers with locations
        suppliers = User.objects.filter(
            user_type='supplier',
            latitude__isnull=False,
            longitude__isnull=False
        ).select_related('supplier_profile')
        
        supplier_list = []
        for supplier in suppliers:
            # Skip if no supplier profile
            if not hasattr(supplier, 'supplier_profile'):
                continue
                
            distance = calculate_distance(
                vendor_lat, vendor_lng,
                float(supplier.latitude), float(supplier.longitude)
            )
            
            supplier_data = {
                'id': supplier.id,
                'user_id': supplier.id,  # ✅ ADD THIS - User ID
                'supplier_id': supplier.supplier_profile.id,  # ✅ ADD THIS - SupplierProfile ID (CRITICAL)
                'name': supplier.supplier_profile.business_name,
                'lat': float(supplier.latitude),
                'lng': float(supplier.longitude),
                'distance': distance,
                'email': supplier.email,
                'phone': supplier.phone_number or 'Not provided',
                'business_type': supplier.supplier_profile.business_type or 'General',
                'items': 'Various items',
                'price': None
            }
            supplier_list.append(supplier_data)
        
        # Sort by distance
        supplier_list.sort(key=lambda x: x['distance'])
        
        return JsonResponse({
            'success': True,
            'suppliers': supplier_list
        })
        
    except Exception as e:
        print(f"❌ Error fetching nearby suppliers: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        
    @api_view(['GET'])
    def all_suppliers(request):
        suppliers = SupplierProfile.objects.select_related('user').all()

        supplier_list = []
        for supplier in suppliers:
            supplier_data = {
                'user_id': supplier.user.id,
                'supplier_id': supplier.id,
                'name': supplier.business_name,
                'username': supplier.user.username,
                'business_type': supplier.business_type or 'General',
            'phone': supplier.phone,
            'email': supplier.user.email,
            'lat': supplier.user.latitude if hasattr(supplier.user, 'latitude') else None,
            'lng': supplier.user.longitude if hasattr(supplier.user, 'longitude') else None,
        }
        supplier_list.append(supplier_data)
    
    return Response({
        'success': True,
        'suppliers': supplier_list,
        'total': len(supplier_list)
    })