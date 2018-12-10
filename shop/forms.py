from django import forms
from .models import Item, Shop


class CreateItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_name', 'price', 'inventory']
        labels = {
            'item_name': '商品名称',
            'prince': '价格',
            'inventory': '库存数量'
        }


class CreateShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['shop_name']
        labels={
            'shop_name': '店铺名'
        }