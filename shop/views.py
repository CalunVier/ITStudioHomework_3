from django.shortcuts import render, reverse, redirect
from .forms import CreateItemForm, CreateShopForm
from .models import ActiveItem, Item, Shop, ActiveShop, Order, OrderShopList
from django.contrib.auth.decorators import login_required
from account.models import UserSeller, UserBuyer, Cart
from django.contrib.auth import authenticate
import os
import json
import decimal

# Create your views here.


def index(request):
    return render(request, 'index.html')


def show_item(request, item_id):
    if request.method == 'GET':
        item = ActiveItem.objects.filter(id=item_id)
        if item:
            item = item[0]
            with open('static/items/'+str(item.item.id)+'/'+str(item.item.version)+'/introduction.intro', 'r') as item_intro_file:
                introduction = item_intro_file.read()
            return render(request, 'item.html', {'item_model': item.item, 'item_introduction': introduction})


@login_required()
def create_item(request):
    seller = UserSeller.objects.filter(user=request.user)
    if seller:
        if request.method == 'GET':
            return render(request, 'createitem.html', {'form': CreateItemForm()})
        if request.method == 'POST':
            form = CreateItemForm(request.POST)
            if form.is_valid():
                item = Item(item_name=form.cleaned_data['item_name'],
                            owner=seller[0],
                            price=form.cleaned_data['price'],
                            inventory=form.cleaned_data['inventory'],
                            active=True
                            )    # 将商品基本信息存入数据库
                item.save()
                ActiveItem(id=item.id, item=item).save()    # 将商品写入Active列表
                intro = request.POST.get('introduction')
                if not os.path.exists('static/items/'+str(item.id)+'/'+str(item.version)+'/'):
                    os.makedirs('static/items/'+str(item.id)+'/'+str(item.version)+'/')
                with open('static/items/'+str(item.id)+'/'+str(item.version)+'/introduction.intro', 'w') as item_introduction_file:
                    item_introduction_file.write(intro)
                return redirect(reverse('shop:ShowItem', args={item.id}))
            return render(request, 'createitem.html', {'form': CreateItemForm(form)})


@login_required
def remove_item(request, item_id):
    if request.method == 'GET':
        item = ActiveItem.objects.filter(id=item_id)
        if item[0].item.owner == UserSeller.objects.filter(request.user):
            item.delete()


def edit_item(request):
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        pass


@login_required()
def create_shop(request):
    seller = UserSeller.objects.filter(request.user)
    if seller:
        if request.method == 'GET':
            return render(request, 'createshop.html', {'create_shop_form': CreateShopForm()})
        if request.method == 'POST':
            form = CreateShopForm(request.POST)
            if form.is_valid():
                shop = Shop(shop_name=form.cleaned_data['shop_name'], owner=seller)
                ActiveShop(id=shop.id, shop=shop)
                return redirect(reverse('shop:VisitMall', {shop.id}))


def edit_shop(request):
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        pass


def remove_shop(request):
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        pass


def visit_shop(request, shop_id):
    if request.method == 'GET':
        shop = Shop.objects.filter(id=shop_id)
        if shop:
            shop = shop[0]
        item_list = None
        if shop:
            item_list = ActiveItem.objects.filter(item__shop=shop)
        return render(request, 'shop.html', {'shop_model': shop, 'item_list': item_list})


def get_editor(request):
    return render('wangEdit\wangEditor.js')


def make_order(request):
    buyer = UserBuyer.objects.filter(user=request.user)
    if buyer:
        buyer = buyer[0]
        order_cart_item_list = Cart.objects.filter(buyer=buyer, collected=False).exclude(item__inventory=0)
        order_item_list_as_json = []
        order_amount = decimal.Decimal(0)
        shops = []
        for cart_item in order_cart_item_list:
            order_amount += cart_item.item.price
            order_item_list_as_json.append({'item_id': cart_item.item.id,
                                            'item_name': cart_item.item.item_name,
                                            'price': cart_item.item.price,
                                            'version': cart_item.item.version})
            if not shops.count(cart_item.item.shop):
                shops.append(cart_item.item.shop)
        # 写入数据库
        order = Order(buyer=buyer, total_amount=order_amount, details=json.dumps(order_item_list_as_json))
        order.save()
        for s in shops:
            OrderShopList(order=0, shop=s).save()
        return


@login_required()
def buyer_pay(request, order_id):
    buyer = UserBuyer.objects.filter(user=request.user)
    if buyer:
        order = Order.objects.filter(id=order_id)
        if order:
            order = order[0]
            if order.buyer == buyer:

                if request.method == 'GET':
                    return render(request, 'pay_page.html', {'allowed': True, 'order': order, 'balance': buyer.balance})
                if request.method == 'POST':
                    if authenticate(username=request.user, password=request.POST.get('password')):
                        buyer -= order.total_amount     # 扣除买家账号余额
                        order.status = 1                # 修改订单状态
                        order.save()
                        order_details = json.loads(order.details)
                        for item in order_details:
                            item = Item.objects.get(id=item['item_id'])
                            item.inventory -= 0
                            item.sales_volume += 1
                            item.save()
                    return redirect(reverse('account:MyOrders'))
            else:
                return render(request, 'pay_page.html', {'allowed': False, 'message': "这不是你的订单"})
        return render(request, 'pay_page.html', {'allowed':False, 'message': "订单不存在"})



