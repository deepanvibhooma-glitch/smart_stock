from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product, Customer, Bill

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Bill)