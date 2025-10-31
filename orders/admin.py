from django.contrib import admin

# Register your models here.
# your_app/admin.py
from django.contrib import admin
from .models import Supplier

admin.site.register(Supplier)
