from django import forms
from .models import Product, Category, Bill, Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'description', 'price', 'stock', 'category', 'status', 'image']

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['customer', 'product', 'quantity']