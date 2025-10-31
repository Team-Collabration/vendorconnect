from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


def index_template(request):
    return render(request, 'index.html')

def vendorlogin_template(request):
    return render(request, 'vendorlogin.html')

def supplierlogin_template(request):
    return render(request, 'supplierlogin.html')

def vendorsignup_template(request):
    return render(request, 'vendorsignup.html')

def suppliersignup_template(request):
    return render(request, 'suppliersignup.html')

def about_template(request):
    return render(request, 'about.html')

def contact_template(request):
    return render(request, 'contact.html')

def suppliers_template(request):
    return render(request, 'suppliers.html')

def suppliers_dashboard_template(request):
    return render(request, 'suppliers-dashboard.html')

def listproducts_template(request):
    return render(request, 'listproducts.html')

def manageorders_template(request):
    return render(request, 'manageorders.html')

def analytics_template(request):
    return render(request, 'analytics.html')

def support_template(request):
    return render(request, 'support.html')

def vendor_dashboard_template(request):
    return render(request, 'vendordashboard.html')

def reviews_template(request):
    return render(request, 'leavereviews.html')

def findsuppliers_template(request):
    return render(request, 'findsuppliers.html')

def compareprices_template(request):
    return render(request, 'compareprices.html')

def order_products_template(request):
    return render(request, 'orderprod.html')

def bulk_template(request):
    return render(request, 'bulk.html')

def place_bulk_order(request):
    if request.method == "POST":
        product = request.POST.get("product")
        quantity = request.POST.get("quantity")
        instructions = request.POST.get("instructions")

        # For now, just display confirmation
        return HttpResponse(f"✅ Order placed: {quantity} units of {product}. Notes: {instructions}")

    # If someone visits the URL directly, show bulk.html
    return redirect("bulk")
from django.http import JsonResponse
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from orders.models import Supplier

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Supplier
import json

@csrf_exempt
def save_supplier_location(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"success": False, "error": "User not logged in"})

        try:
            data = json.loads(request.body)
            lat = data.get("lat")
            lng = data.get("lng")
        except:
            return JsonResponse({"success": False, "error": "Invalid JSON"})

        if lat is None or lng is None:
            return JsonResponse({"success": False, "error": "Latitude or Longitude missing"})

        # Get or create Supplier object for this user
        supplier, created = Supplier.objects.get_or_create(user=user, defaults={"name": user.username})
        supplier.lat = lat
        supplier.lng = lng
        supplier.save()

        return JsonResponse({"success": True, "message": "Location saved!"})

    return JsonResponse({"success": False, "error": "Invalid request"})


# vendorconnect_backend/views.py
from orders.models import Supplier
from django.http import JsonResponse

def all_suppliers(request):
    suppliers = Supplier.objects.filter(lat__isnull=False, lng__isnull=False)
    data = []
    for s in suppliers:
        data.append({
            "id": s.id,
            "name": s.name,
            "lat": s.lat,
            "lng": s.lng,
            "items": s.items,
            "price": s.price
        })
    return JsonResponse({"suppliers": data})



from django.shortcuts import render, redirect
from reviews.models import ContactMessage
from django.contrib import messages

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')  # reloads page or redirect to success
    return render(request, 'contact.html')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi:latest"  # use the model you pulled

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message", "")

        payload = {
            "model": MODEL_NAME,
            "prompt": message,
            "stream": False
        }

        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=30)
            result = response.json().get("response", "Sorry, I couldn't process that.")
        except Exception as e:
            result = f"Error: {str(e)}"

        return JsonResponse({"reply": result})


 #In your main vendorconnect_backend/views.py file
from products.views import compareprices as compareprices_view

@login_required
def compareprices_template(request):
    """Wrapper for compareprices view"""
    return compareprices_view(request)

def vendor_orders_template(request):
    return render(request, 'orders.html')