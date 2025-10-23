#!/usr/bin/env python3
"""
API test script for VendorConnect backend
Supports both vendor and supplier signup.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"


# -------------------------
# Helper Functions
# -------------------------

def print_response(response):
    """Utility to print response details"""
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:", json.dumps(response.json(), indent=2))
    except:
        print("Response Text:", response.text)


# -------------------------
# Test Endpoints
# -------------------------

def test_categories():
    print("\nTesting categories endpoint...")
    response = requests.get(f"{BASE_URL}/products/categories/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Categories endpoint working. Found {len(data)} categories:")
        for category in data:
            print(f"  - {category['name']}")
    else:
        print("❌ Categories endpoint failed")
        print_response(response)


def test_products():
    print("\nTesting products endpoint...")
    response = requests.get(f"{BASE_URL}/products/products/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Products endpoint working. Found {len(data['results'])} products:")
        for product in data['results'][:5]:
            print(f"  - {product['name']} ({product['unit']})")
    else:
        print("❌ Products endpoint failed")
        print_response(response)


def test_supplier_products():
    print("\nTesting supplier products endpoint...")
    response = requests.get(f"{BASE_URL}/products/supplier-products/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Supplier products endpoint working. Found {len(data['results'])} supplier products:")
        for sp in data['results'][:5]:
            print(f"  - {sp['product_name']} by {sp['supplier']['business_name']} (₹{sp['price']})")
    else:
        print("❌ Supplier products endpoint failed")
        print_response(response)


# -------------------------
# Authentication Tests
# -------------------------

def test_vendor_signup():
    """Test vendor signup"""
    print("\nTesting vendor signup...")
    user_data = {
        "username": "testvendor",
        "email": "testvendor@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "user_type": "vendor",
        "phone_number": "+919876543214",
        "business_name": "Test Vendor",
        "business_type": "Street Food",
        "address": "Test Address",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001"
    }
    response = requests.post(f"{BASE_URL}/accounts/vendors/signup/", json=user_data)
    if response.status_code in [200, 201]:
        print("✅ Vendor signup successful")
        print_response(response)
    else:
        print("❌ Vendor signup failed")
        print_response(response)


def test_supplier_signup():
    """Test supplier signup"""
    print("\nTesting supplier signup...")
    user_data = {
        "username": "testsupplier",
        "email": "testsupplier@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "user_type": "supplier",
        "phone_number": "+919812345678",
        "business_name": "Test Supplier",
        "business_type": "Grocery",
        "address": "Supplier Address",
        "city": "Delhi",
        "state": "Delhi",
        "pincode": "110001"
    }
    response = requests.post(f"{BASE_URL}/accounts/supplier/signup/", json=user_data)
    if response.status_code in [200, 201]:
        print("✅ Supplier signup successful")
        print_response(response)
    else:
        print("❌ Supplier signup failed")
        print_response(response)


def test_user_login(username="testvendor", password="testpass123"):
    print("\nTesting user login...")
    login_data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/accounts/login/", json=login_data)
    if response.status_code == 200:
        print("✅ User login successful")
        print_response(response)
        return response.json().get('user', {}).get('id')
    else:
        print("❌ User login failed")
        print_response(response)
        return None


def test_product_search():
    print("\nTesting product search...")
    search_data = {"query": "tomatoes", "min_price": 20, "max_price": 100}
    response = requests.post(f"{BASE_URL}/products/search/", json=search_data)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Product search working. Found {len(data)} results")
    else:
        print("❌ Product search failed")
        print_response(response)


# -------------------------
# Main
# -------------------------

def main():
    print("🚀 Testing VendorConnect Backend API")
    print("=" * 50)

    # Test endpoints
    test_categories()
    test_products()
    test_supplier_products()

    # Test signups
    test_vendor_signup()
    test_supplier_signup()

    # Test login
    test_user_login("testvendor", "testpass123")
    test_user_login("testsupplier", "testpass123")

    # Test product search
    test_product_search()

    print("\n" + "=" * 50)
    print("✅ API testing completed!")


if __name__ == "__main__":
    main()
