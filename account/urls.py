"""E_commerce_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^register/', views.register, name='Register'),
    url(r'^login/', views.login, name='Login'),
    url(r'^logout/', views.logout, name='Logout'),
    url(r'^changepw/', views.change_password, name='ChangePassword'),
    url(r'^my_orders', views.my_orders, name='MyOrders'),
    url(r'^buyer/home/', views.buyer_home, name='BuyerHome'),
    url(r'^seller/home/', views.seller_home, name='SellerHome'),
    url(r'^seller/my_items/', views.my_items, name='MyItems'),
    url(r'^seller/my_mall/', views.my_mall, name='MyMall'),
]
