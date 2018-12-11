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
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create_item/', views.create_item, name='CreateItem'),
    url(r'^item/(\d+)', views.show_item, name='ShowItem'),
    url(r'^remove_item/(\d+)', views.remove_item, name='RemoveItem'),
    url(r'^create_mall/', views.create_shop, name='CreateMall'),
    url(r'^delete_mall/(\d+)', views.remove_shop, name='DeleteMall'),
    url(r'^mall/(\d+)', views.visit_shop, name='VisitMall'),
    url(r'^cart/', views.cart, name='Cart')
    # url(r'^order/(\d+)', name='Order'),
    # url(r'^pay_page/(\d+)', name='PayPage')
]
