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
    url(r'^cart/', views.cart, name='Cart'),
    url(r'^get_valid_code_img/(.+)', views.get_valid_code_img, name='GetValidCodeImg'),
    url(r'^delete_item_from_cart/(\d+)', views.delete_item_form_cart, name='DeleteItemFormCart'),
    url(r'^add_item_to_collection/(\d+)', views.add_item_to_collection, name='AddItemToCollection'),
    url(r'^form_collection_add_to_cart/(\d+)', views.form_collection_add_to_cart, name='FormCollectionAddToCart'),
    url(r'^order/(\d+)', views.order_details, name='Order'),
    url(r'^pay_page/(\d+)', views.buyer_pay, name='PayPage'),
    url(r'^history/item/(\d+)/(\d+)', views.history_item, name='HistoryItem'),
    url(r'^buyer/make_order/(\d+)?', views.make_order, name='MakeOrder'),
    url(r'^order_operation/(\d+)/(\d)', views.order_operation, name='OrderOperation'),
    url(r'^edit_item/(\d+)', views.edit_item, name='EditItem'),
]
