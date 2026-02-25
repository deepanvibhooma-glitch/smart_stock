"""
URL configuration for smartproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from smartapp import views

urlpatterns = [
    path('land', views.landing_view, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.products, name='products'),
    path('save_products/', views.save_products, name='save_products'),
    path('search/', views.global_search, name='global_search'),
    path('customers/', views.customers, name='customers'),
    path('billing/', views.billing, name='billing'),
    path('save_bill/', views.save_bill, name='save_bill'),
    path('dashboard2/', views.dashboard2, name='dashboard2'),
    path('products2/', views.products2, name='products2'),
    path('categories/', views.categories_view, name='categories_view'),
    path('api/add-category/', views.api_add_category, name='api_add_category'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('add-product/', views.add_product_view, name='add_product_view'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('customers2/', views.customers2_view, name='customers2'),
    path('billing2/', views.billing2_view, name='billing2'),
    path('settings/', views.settings_view, name='settings_view'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]
