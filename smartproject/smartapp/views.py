from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncMonth
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Category, Product, Customer, Bill, StoreSettings
from .forms import CategoryForm, ProductForm, CustomerForm

@csrf_exempt
def api_add_category(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')
            
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Category name is required'})
                
            category = Category.objects.create(name=name, description=description)
            return JsonResponse({
                'status': 'success', 
                'category': {
                    'id': category.id,
                    'name': category.name
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid request'}, status=400)

@login_required
def dashboard(request):
    # Stats Calculation
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    
    # Revenue this month
    now = timezone.now()
    month_revenue = Bill.objects.filter(
        bill_date__year=now.year, 
        bill_date__month=now.month
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Low stock alerts (arbitrary threshold like <= 5)
    low_stock_count = Product.objects.filter(stock__lte=5).count()
    
    # Inventory Overview Categories calculation
    # Using Django ORM to aggregate live products inside categories matching requirements
    categories = Category.objects.annotate(
        total_products=Count('products'),
        total_stock=Sum('products__stock'),
        low_stock=Count('products', filter=Q(products__stock__lte=5))
    )[:8]
        
    # Recent Activity Extraction (Fetch last 4 bills for demo activity trace)
    recent_activity = []
    bills = Bill.objects.order_by('-bill_date')[:4]
    for b in bills:
        recent_activity.append(
            f"✔ Invoice #{b.id} generated for {b.customer.name} (₹{b.total_price})"
        )

    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'month_revenue': month_revenue,
        'low_stock_count': low_stock_count,
        'categories': categories,
        'recent_activity': recent_activity
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def products(request):
    category_form = CategoryForm()
    product_form = ProductForm()

    if request.method == "POST":
        # Create Category
        if 'category_name' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                return redirect('products')
        # Add Product
        elif 'product_name' in request.POST:
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product_form.save()
                return redirect('products')

    categories = Category.objects.all().prefetch_related('products')
    products = Product.objects.all()

    return render(request, 'products.html', {
        'category_form': category_form,
        'product_form': product_form,
        'categories': categories,
        'products': products
    })

@csrf_exempt
@login_required
def save_products(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            saved_names = []
            for item in data:
                name = item.get('name')
                stock = item.get('stock')
                price = item.get('price')
                
                if name:
                    saved_names.append(name)
                    # Check if product exists to update it, else create
                    product, created = Product.objects.get_or_create(
                        name=name, 
                        defaults={'stock': stock, 'price': price}
                    )
                    if not created:
                        product.stock = stock
                        product.price = price
                        product.save()
            
            # Delete any products that were removed from the table 
            Product.objects.exclude(name__in=saved_names).delete()
                        
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid request'})

@login_required
def customers(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customers')
    
    # Calculate total purchases (number of bills/items bought by customer)
    # the frontend expects 'total_purchases'
    customers_list = Customer.objects.annotate(
        total_purchases=Count('bill')
    )
    
    # Filter customers with more than 5 purchases to be "regular customers"
    regular_customers = customers_list.filter(total_purchases__gte=5)
    
    return render(request, 'customers.html', {
        'customers': customers_list,
        'regular_customers': regular_customers
    })

@login_required
def global_search(request):
    query = request.GET.get('q', '')
    results = []
    
    try:
        if query:
            # Search products
            products = Product.objects.filter(name__icontains=query)[:5]
            for p in products:
                results.append({
                    'id': p.id,
                    'name': p.name,
                    'type': 'product',
                    'image': p.image_url
                })
                
            # Search customers
            customers = Customer.objects.filter(name__icontains=query)[:5]
            for c in customers:
                results.append({
                    'id': c.id,
                    'name': c.name,
                    'type': 'customer'
                })

            # Search categories
            try:
                categories = Category.objects.filter(name__icontains=query)[:5]
                for cat in categories:
                    results.append({
                        'id': cat.id,
                        'name': cat.name,
                        'type': 'category'
                    })
            except:
                pass # Categories might be broken or missing name field
                
        return JsonResponse({'results': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def landing_view(request):
    # Fetch some data for the landing page
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_categories = Category.objects.count()
    total_revenue = Bill.objects.aggregate(total=Sum('total_price'))['total'] or 0

    # Get a few recent products
    recent_products = Product.objects.order_by('-id')[:5]

    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_categories': total_categories,
        'total_revenue': total_revenue,
        'recent_products': recent_products,
    }
    return render(request, 'landing.html', context)

@login_required
def billing(request):
    return render(request, 'billing.html')

def billing2_view(request):
    # Fetch data for billing context
    products = Product.objects.all().defer('sku', 'description', 'status')
    customers = Customer.objects.all()
    recent_bills = Bill.objects.select_related('customer', 'product').all().order_by('-id')[:10]
    
    context = {
        'products': products,
        'customers': customers,
        'recent_bills': recent_bills,
        'total_sales': Bill.objects.aggregate(total=Sum('total_price'))['total'] or 0,
        'total_bills': Bill.objects.count(),
    }
    return render(request, 'billing2.html', context)

@csrf_exempt
@login_required
def save_bill(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            customer_name = data.get('customer')
            phone = data.get('phone')
            items = data.get('items', [])
            
            if not customer_name or not items:
                return JsonResponse({'status': 'error', 'message': 'Missing customer or items'})
                
            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                name=customer_name
            )
            
            # Update phone if provided
            if phone:
                customer.phone = phone
                customer.save()
            
            # Process items
            for item in items:
                product_name = item.get('name')
                qty = item.get('qty', 0)
                price = item.get('price', 0)
                
                # Deduct stock safely if product exists, otherwise ignore or log error
                product = Product.objects.filter(name=product_name).first()
                if product:
                    product.stock = max(0, product.stock - qty)
                    product.save()
                else:
                    # If product wasn't in DB, handle appropriately. For safety we can create a dummy one
                    # but usually it's better to just skip or log.
                    product, _ = Product.objects.get_or_create(
                        name=product_name,
                        defaults={'price': price, 'stock': 0}
                    )
                
                # Calculate total for exactly this item line
                line_total_price = qty * price
                
                # Add a Bill row
                Bill.objects.create(
                    customer=customer,
                    product=product,
                    quantity=qty,
                    total_price=line_total_price
                )
                        
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'invalid request'})

@login_required
def dashboard2(request):
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(stock__lte=5).count()
    total_categories = Category.objects.count()
    total_revenue = Bill.objects.aggregate(total=Sum('total_price'))['total'] or 0
    
    # Recent products for the inventory table (deferring new fields until migrations)
    recent_products = Product.objects.select_related('category').defer('sku', 'description', 'status').all().order_by('-id')[:6]
    
    # Chart Data: Monthly Sales for the last 6 months
    six_months_ago = timezone.now() - timezone.timedelta(days=180)
    sales_data = Bill.objects.filter(bill_date__gte=six_months_ago) \
        .annotate(month=TruncMonth('bill_date')) \
        .values('month') \
        .annotate(total=Sum('total_price')) \
        .order_by('month')
    
    chart_labels = [data['month'].strftime('%b') for data in sales_data]
    chart_data = [float(data['total']) for data in sales_data]
    
    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_categories': total_categories,
        'total_revenue': total_revenue,
        'recent_products': recent_products,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'dashboard2.html', context)

@login_required
def products2(request):
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(stock__range=(1, 5)).count()
    out_of_stock_count = Product.objects.filter(stock=0).count()
    
    # Fetch all products with their categories (deferring new fields until migrations are run)
    products = Product.objects.select_related('category').defer('sku', 'description', 'status').all().order_by('-id')
    
    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'products': products
    }
    return render(request, 'products2.html', context)

@login_required
def categories_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            Category.objects.create(name=name, description=description)
            return redirect('categories_view')

    # Fetch all categories with product counts
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-id')
    
    total_categories = categories.count()
    
    # Most Used Category (one with highest product count)
    most_used_category = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count').first()
    
    # Recently Added Category
    recently_added = Category.objects.order_by('-id').first()
    
    context = {
        'categories': categories,
        'total_categories': total_categories,
        'most_used_category': most_used_category,
        'recently_added': recently_added,
    }
    return render(request, 'categories.html', context)

@login_required
def delete_category(request, category_id):
    category = Category.objects.filter(id=category_id).first()
    if category:
        category.delete()
    return redirect('categories_view')

from django.contrib import messages
from django.db import IntegrityError

@login_required
def add_product_view(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                return redirect('products2')
            except IntegrityError:
                messages.error(request, "A product with this SKU already exists.")
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
                    
    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        messages.success(request, f"Product '{product.name}' deleted successfully.")
    return redirect('products2')

def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'login_signup.html', {'signup': True})
            
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
        login(request, user)
        messages.success(request, f"Welcome to SmartStock, {first_name}!")
        return redirect('dashboard2')
    return render(request, 'login_signup.html', {'signup': True})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('dashboard2')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login_signup.html', {'signup': False})
    return render(request, 'login_signup.html', {'signup': False})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('landing')

@login_required
def customers2_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        
        if name and phone:
            Customer.objects.create(name=name, phone=phone, email=email)
            return redirect('customers2')

    # Enhanced stats
    customers_list = Customer.objects.annotate(
        total_purchases=Count('bill')
    ).order_by('-id')
    
    total_customers = customers_list.count()
    regular_customers_count = customers_list.filter(total_purchases__gt=0).count()
    
    # New customers today
    today = timezone.now().date()
    new_today = Customer.objects.filter(created_at__date=today).count()
    
    # Regular customers for the highlight section (Top buyers)
    regular_customers = customers_list.filter(total_purchases__gt=0).order_by('-total_purchases')[:3]

    context = {
        'customers': customers_list,
        'total_customers': total_customers,
        'regular_customers_count': regular_customers_count,
        'new_today': new_today,
        'regular_customers': regular_customers,
    }
    return render(request, 'customers2.html', context)

@login_required
def settings_view(request):
    settings, _ = StoreSettings.objects.get_or_create(id=1)
    
    if request.method == "POST":
        settings.store_name = request.POST.get('store_name', settings.store_name)
        settings.owner_name = request.POST.get('owner_name', settings.owner_name)
        settings.phone = request.POST.get('phone', settings.phone)
        settings.email = request.POST.get('email', settings.email)
        settings.address = request.POST.get('address', settings.address)
        settings.gst_number = request.POST.get('gst_number', settings.gst_number)
        settings.default_tax_rate = request.POST.get('tax_rate', settings.default_tax_rate)
        settings.save()
        return redirect('settings_view')

    return render(request, 'settings.html', {'settings': settings})
