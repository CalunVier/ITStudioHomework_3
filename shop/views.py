from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from .forms import CreateItemForm, CreateShopForm
from .models import ActiveItem, Item, Shop, ActiveShop, Order, Cart, BuyerAndItem
from django.contrib.auth.decorators import login_required
from account.models import UserSeller, UserBuyer
from account.views import get_user_type, get_status_bar, valid_code_data
from django.contrib.auth import authenticate
import os
import json
import decimal
import datetime


# 主页
def index(request):
    return render(request, 'index.html', {'status': get_status_bar(request)})


# 商品页面
def show_item(request, item_id):
    active_item = ActiveItem.objects.filter(id=item_id)
    if active_item:
        active_item = active_item[0]
        user, user_type = get_user_type(request.user)
        if request.method == 'GET':

            if os.path.exists('static/items/'+str(active_item.item.item_id)+'/'+str(active_item.item.version)+'/introduction.intro'):
                with open('static/items/'+str(active_item.item.item_id)+'/'+str(active_item.item.version)+'/introduction.intro', 'r') as item_intro_file:
                    introduction = item_intro_file.read()
            else:
                introduction = ''
            print(user_type)
            return render(request, 'item.html',
                          {'item_model': active_item.item, 'item_introduction': introduction,
                           'status_bar': get_status_bar(request),
                           'user_type': user_type})
        if request.method == 'POST':
            if user_type == 'buyer':
                print(request.POST.get('add_to_cart'))
                if request.POST.get('add_to_cart'):     # 如果选择添加到购物车
                    cart_item = Cart.objects.filter(user=user, item__item_id=active_item.id)
                    if cart_item:
                        cart_item[0].quantity += 1
                        cart_item[0].save()
                    else:
                        Cart(user=user, item=active_item.item).save()
                    return render(request, 'message.html',
                                  {'status_bar':get_status_bar(request),
                                   'message_title': '购物车添加成功',
                                   'message': '已经成功将商品添加到您的购物车',
                                   'other': '<a href="/shop/item/{0}">返回</a>'.format(str(item_id))})
                elif request.POST.get('buy_now'):   # 如果选择直接购买
                    return redirect(reverse('shop:MakeOrder', args=[item_id]))
                else:   # 以其他未知方式提交表单
                    return HttpResponse(status=403)
            elif not user_type:     # 如果未登录，或因其他原因返回none
                return redirect(reverse('account:Login'))
            elif user_type == 'seller':
                return HttpResponse(status=403)
            else:   # 如果出现其他未知原因
                return HttpResponse(status=403)

    else:
        HttpResponse(status=404)


# 创建商品
@login_required()
def create_item(request):
    seller = UserSeller.objects.filter(user=request.user)
    if seller:
        if request.method == 'GET':
            choice = [(0, '无')]
            shops = Shop.objects.filter(owner=seller)
            for shop in shops:
                choice.append((shop.id, shop.shop_name))
            return render(request, 'createitem.html', {'form': CreateItemForm(), 'choices': choice})
        if request.method == 'POST':
            form = CreateItemForm(request.POST)
            if form.is_valid():
                item = Item(item_name=form.cleaned_data['item_name'],
                            owner=seller[0],
                            price=form.cleaned_data['price'],
                            inventory=form.cleaned_data['inventory'],
                            active=True
                            )    # 将商品基本信息存入数据库
                try:
                    shop = int(request.POST.get('shop'))
                except ValueError:
                    shop = 0
                if shop:
                    shop = Shop.objects.filter(id=shop)
                    if shop:
                        item.shop = shop[0]
                item.save()
                item.item_id = item.id
                print(item.id)
                item.save()
                ActiveItem(id=item.item_id, item=item).save()    # 将商品写入Active列表

                # 开始写入商品介绍
                # 商品介绍将被写入static/items/<item_id>/<item_version>/introduction.intro文件
                # 商品介绍为html文本
                intro = request.POST.get('introduction')
                # 判断有关文件夹是否存在，如果没有，则创建
                if not os.path.exists('static/items/'+str(item.item_id)+'/'+str(item.version)+'/'):
                    os.makedirs('static/items/'+str(item.item_id)+'/'+str(item.version)+'/')
                with open('static/items/'+str(item.item_id)+'/'+str(item.version)+'/introduction.intro', 'w') as item_introduction_file:
                    item_introduction_file.write(intro)
                return redirect(reverse('shop:ShowItem', args=[item.id]))   # 创建成功，重定向到商品页面
            return render(request, 'createitem.html', {'form': CreateItemForm(form)})   # 注册失败，重新返回本页面


# 删除商品view
@login_required
def remove_item(request, item_id):
    if request.method == 'GET':
        user, user_type = get_user_type(request.user)
        if user_type == 'seller':
            item = ActiveItem.objects.filter(id=item_id)
            if item:
                if item[0].item.owner == user:
                    item[0].item.active = False
                    item[0].item.save()
                    item.delete()
        else:
            return render(request, 'message.html', {'message_title': '删除失败', 'message': '这不是你的商品'})


# 修改商品
@login_required()
def edit_item(request, item_id):
    if request.method == 'GET':
        active_item = ActiveItem.objects.filter(id=item_id)
        if active_item:
            item = active_item[0].item
            if not os.path.exists('static/items/' + str(item.item_id) + '/' + str(item.version) + '/'):
                os.makedirs('static/items/' + str(item.item_id) + '/' + str(item.version) + '/')
            with open('static/items/' + str(item.item_id) + '/' + str(item.version) + '/introduction.intro',
                      'r') as item_introduction_file:
                introduction = item_introduction_file.read()
            # form = CreateItemForm()
            # form.item_name = item.item_name
            # form.price = item.price
            # form.inventory = item.inventory
            return render(request, 'edit_item.html', {'status_bar':get_status_bar(request),
                                                      'item_name':item.item_name,
                                                      'price': str(item.price),
                                                      'inventory': str(item.inventory),
                                                       'introduction': introduction})
    if request.method == 'POST':
        pass


def delete_item(request, item_id):
    pass

# 创建店铺
@login_required()
def create_shop(request):
    seller = UserSeller.objects.filter(user=request.user)
    if seller:
        if request.method == 'GET':
            return render(request, 'createshop.html', {'create_shop_form': CreateShopForm(), 'status_bar': get_status_bar(request)})
        if request.method == 'POST':
            form = CreateShopForm(request.POST)
            if form.is_valid():
                shop = Shop(shop_name=form.cleaned_data['shop_name'], owner=seller[0])
                shop.save()
                ActiveShop(id=shop.id, shop=shop).save()
                return redirect(reverse('shop:VisitMall', args=[shop.id]))


# 修改店铺信息
@login_required()
def edit_shop(request, shop_id):
    seller, user_type = get_user_type(request.user)
    if user_type == 'seller':
        if request.method == 'GET':
            active_shop = ActiveShop.objects.filter(id=shop_id)     # 在活动shop中检索shop
            if active_shop:     # 若存在
                if active_shop[0].shop.owner == seller:     # 检查该商店是否属于操作者
                    return render(request, 'createshop.html', {'create_shop_form': CreateShopForm(active_shop[0])})
                else:
                    return render(request, 'message.html', {'message_title': '这不是你的店铺', 'message': '这不是你的店铺'})
            else:
                return render(request, 'message.html', {'message_title': '没有找到店铺', 'message': '没有找到对应的店铺'})

        if request.method == 'POST':
            active_shop = ActiveShop.objects.filter(id=shop_id)     # 在活动shop中检索shop
            if active_shop:     # 若存在
                if active_shop[0].shop.owner == seller:     # 检查该商店是否属于操作者
                    form = CreateShopForm(request.POST)
                    # 下面这一段注释不明觉厉，我没有给shop添加版本号为什么要这样写
                    # new_shop = Shop(shop_id=active_shop[0].shop.shop_id,
                    #                 shop_name=form.cleaned_data['shop_name'],
                    #                 owner=active_shop[0].shop.owner,
                    #                 sales_amount=active_shop[0].shop.sales_amount,
                    #                 sales_volume=active_shop[0].shop.sales_volume,
                    #                 create_time=active_shop[0].shop.create_time)
                    # new_shop.save()
                    # active_shop[0].shop = new_shop
                    # active_shop.update()
                    active_shop[0].shop.shop_name = form.cleaned_data['shop_name']      # 修改商店名
                    active_shop[0].shop.save()      # 更新数据库
                    return redirect(reverse('shop:VisitMall', args=[shop_id]))
                else:
                    return render(request, 'message.html', {'message_title': '这不是你的店铺', 'message': '这不是你的店铺'})
            else:
                return render(request, 'message.html', {'message_title': '没有找到店铺', 'message': '没有找到对应的店铺'})
    else:
        return render(request, 'message.html', {'message_title': '你不是卖家', 'message': '你不是卖家'})


# 删除店铺
def remove_shop(request, shop_id):
    seller, user_type = get_user_type(request.user)
    if user_type == 'seller':   # 检查用户是否为卖家
        if request.method == 'GET':
            active_shop = ActiveShop.objects.filter(id=shop_id)  # 在活动shop中检索shop
            if active_shop:  # 若存在
                if active_shop[0].shop.owner == seller:  # 检查该商店是否属于操作者
                    active_shop.delete()
                    return redirect(reverse('Index'))
                else:   # 若不属于
                    return render(request, 'message.html', {'message_title': '这不是你的店铺', 'message': '这不是你的店铺'})
            else:   # 若存在
                return render(request, 'message.html', {'message_title': '没有找到店铺', 'message': '没有找到对应的店铺'})
    else:
        return render(request, 'message.html', {'message_title': '你不是卖家', 'message': '你不是卖家'})


# 浏览店铺
def visit_shop(request, shop_id):
    if request.method == 'GET':
        shop = Shop.objects.filter(id=shop_id)
        if shop:
            shop = shop[0]
        item_list = None
        if shop:
            item_list = ActiveItem.objects.filter(item__shop=shop)
        return render(request, 'shop.html', {'status_bar': get_status_bar(request), 'shop_model': shop, 'item_list': item_list})


# 获取富文本编辑器？？？？
# def get_editor(request):
#     return render('wangEdit\wangEditor.js')

# 创建订单
@login_required()
def make_order(request, item_id):
    buyer = UserBuyer.objects.filter(user=request.user)
    try:
        item_id = int(item_id)
    except BaseException:
        item_id = 0
    if request.method == 'GET':
        if buyer:
            buyer = buyer[0]
            if item_id:
                item = ActiveItem.objects.filter(id=item_id)[0].item
                order_cart_item_list = [Cart(user=buyer, collected=False, item=item, quantity=1)]
            else:
                # 获取cart中所有的item，除去收集的，没有货的，和不活动的item
                order_cart_item_list = Cart.objects.filter(user=buyer, collected=False).exclude(item__inventory=0).exclude(
                    item__active=False)
            if order_cart_item_list:
                orders = {}     # 临时存储订单
                for cart_item in order_cart_item_list:
                    if cart_item.item.shop.id not in orders.keys():     # 如果没有为该店铺建立订单
                        orders[cart_item.item.shop.id] = Order(buyer=buyer, shop=cart_item.item.shop)
                        orders[cart_item.item.shop.id].details = []
                    orders[cart_item.item.shop.id].total_amount += cart_item.item.price
                    orders[cart_item.item.shop.id].details.append({'item_id': cart_item.item.item_id,  # 商品id
                                                                   'item_name': cart_item.item.item_name,  # 商品名
                                                                   'price': str(cart_item.item.price),  # 销售时的商品价格
                                                                   'version': cart_item.item.version,
                                                                   'quantity': cart_item.quantity})  # 商品版本
                return render(request, 'make_order.html', {'status_bar': get_status_bar(request),'orders': orders,
                                                           'item_id': item_id})
            else:
                return render(request, 'message.html', {'message_title': '没有商品',
                                                        'message': '您的购物车为空，无法创建订单',
                                                        'status_bar': get_status_bar(request)})
    if request.method == 'POST':
        if buyer:
            buyer = buyer[0]
            if item_id:
                item = ActiveItem.objects.filter(id=item_id)[0].item
                order_cart_item_list = [Cart(user=buyer, collected=False, item=item, quantity=1)]
            else:
                # 获取cart中所有的item，除去收集的，没有货的，和不活动的item
                order_cart_item_list = Cart.objects.filter(user=buyer, collected=False).exclude(item__inventory=0).exclude(item__active=False)
            if order_cart_item_list:    # 如果存在
                # order_item_list_as_json = []    # 存储json化的订单信息
                # order_amount = decimal.Decimal(0)
                # shops = []      # 保存涉及的店铺
                orders = {}
                orders_details = {}
                for cart_item in order_cart_item_list:
                    if cart_item.item.shop.id not in orders.keys():
                        orders[cart_item.item.shop.id] = Order(buyer=buyer, shop=cart_item.item.shop)
                        orders_details[cart_item.item.shop.id] = []
                    orders[cart_item.item.shop.id].total_amount += cart_item.item.price
                    orders_details[cart_item.item.shop.id].append({'item_id': cart_item.item.item_id,           # 商品id
                                                                    'item_name': cart_item.item.item_name,  # 商品名
                                                                    'price': str(cart_item.item.price),          # 销售时的商品价格
                                                                    'version': cart_item.item.version,
                                                                    'quantity': cart_item.quantity})     # 商品版本
                    # 库存信息处理
                    cart_item.item.inventory -= 1
                    cart_item.item.sales_volume += 1
                    cart_item.item.save()

                    # 店铺信息更新
                    cart_item.item.shop.sales_volume += 1
                    cart_item.item.shop.sales_amount += cart_item.item.price
                    cart_item.item.shop.save()
                # 将订单们写入数据库
                orders_key = orders.keys()
                for key in orders_key:
                    orders[key].details = json.dumps(orders_details[key])
                    orders[key].save()


                # # 写入数据库
                # order = Order(buyer=buyer, total_amount=order_amount, details=json.dumps(order_item_list_as_json))
                # order.save()
                # for s in shops:
                #     OrderShopList(order=order, shop=s).save()
                try:
                    order_cart_item_list.delete()
                except AttributeError:
                    pass
                if len(orders) == 1:
                    for key in orders.keys():
                        order_id = orders[key].id
                    return redirect(reverse('shop:PayPage', args=[order_id]))
                elif len(orders) > 1:
                    return redirect(reverse('account:MyOrders'))
                else:
                    return HttpResponse(status=503)
            else:
                return render(request, 'message.html', {'message_title': '没有商品',
                                                        'message': '您的购物车为空，无法创建订单',
                                                        'status_bar': get_status_bar(request)})
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=404)


# 支付
@login_required()
def buyer_pay(request, order_id):
    buyer = UserBuyer.objects.filter(user=request.user)
    if buyer:
        order = Order.objects.filter(id=order_id)
        if order:
            order = order[0]
            if order.status == 0:
                if order.buyer == buyer[0]:
                    if request.method == 'GET':
                        return render(request, 'pay_page.html', {'order': order, 'balance': buyer[0].balance})
                    if request.method == 'POST':
                        if authenticate(username=request.user, password=request.POST.get('password')):
                            buyer[0].balance -= order.total_amount     # 扣除买家账号余额
                            buyer[0].save()
                            order.status = 1                # 修改订单状态
                            order.last_edit = datetime.datetime.now()
                            order.save()
                            return redirect(reverse('account:MyOrders'))
                        else:
                            return render(request, 'pay_page.html', {'order': order, 'balance': buyer[0].balance,
                                                                     'message': '密码错误'})
                else:
                    return render(request, 'pay_page.html', {'allowed': False, 'message': "这不是你的订单"})
            else:
                return HttpResponse(status=403)
        return render(request, 'pay_page.html', {'allowed': False, 'message': "订单不存在"})


# 购物车（买家）
@login_required()
def cart(request):
    user, user_type = get_user_type(request.user)
    if user_type == 'buyer':
        cart_item_list = Cart.objects.filter(user=user)
        # for 检查购物车中的Item是否为active，同时尝试替换为最新版本
        for cart_item in cart_item_list:
            if not cart_item.item.active:   # 检查购物车中保存的版本是否active
                # 若不是最新
                # 检索ActiveItem
                active_item_queryset = ActiveItem.objects.filter(id=cart_item.item.item_id)
                if active_item_queryset:    # 若存在新版本
                    cart_item.item = active_item_queryset[0].item
                    cart_item.save()
        return render(request, 'buyer_cart.html', {'cart_item_list': cart_item_list, 'status_bar': get_status_bar(request)})
    else:
        return render(request, 'message.html', {'message_title': '您不是买家', 'message': '您不是买家，无法查看购物车'})


# 从购物车删除商品
@login_required()
def delete_item_form_cart(request, item_id):
    buyer, user_type = get_user_type(request.user)
    if user_type == 'buyer':
        cart_item = Cart.objects.filter(user=buyer, item__item_id=item_id)
        if cart_item:
            cart_item.delete()
            return redirect(reverse('shop:Cart'))
        else:
            return HttpResponse(status=403)
    else:   # 不需要给攻击者提供用户体验233333直接403
        return HttpResponse(status=403)


# 将购物车内商品添加到收藏列表
@login_required()
def add_item_to_collection(request, item_id):
    if request.method == 'GET':
        buyer, user_type = get_user_type(request.user)
        if user_type == 'buyer':
            cart_item = Cart.objects.filter(user=buyer, item__item_id=item_id)
            if cart_item:
                cart_item[0].collected = True
                cart_item[0].save()
                return redirect(reverse('shop:Cart'))
            else:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)


# 获取验证码
def get_valid_code_img(request, hash_valid_str):
    if request.method == 'GET':
        if hash_valid_str in valid_code_data.keys():
            response = HttpResponse(valid_code_data[hash_valid_str])
            del valid_code_data[hash_valid_str]
            if len(valid_code_data) > 500:
                valid_code_data.clear()
            return response
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=403)


# 从收藏列表添加到购物车
@login_required()
def form_collection_add_to_cart(request, item_id):
    if request.method == 'GET':
        buyer, user_type = get_user_type(request.user)
        if user_type == 'buyer':
            cart_item = Cart.objects.filter(user=buyer, item__item_id=item_id)
            if cart_item:
                cart_item[0].collected = False
                cart_item[0].save()
                return redirect(reverse('shop:Cart'))
            else:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)


# 历史商品
def history_item(request, item_id, version):
    if request.method == 'GET':
        item = Item.objects.filter(item_id=item_id, version=version)
        if item:
            item = item[0]
            if os.path.exists('static/items/' + str(item.item_id) + '/' + str(
                    item.version) + '/introduction.intro'):
                with open('static/items/' + str(item.item_id) + '/' + str(
                        item.version) + '/introduction.intro', 'r') as item_intro_file:
                    introduction = item_intro_file.read()
            else:
                introduction = ''
            return render(request, 'item.html',
                          {'item_model': item, 'item_introduction': introduction,
                           'status_bar': get_status_bar(request),
                           'history': True})
        else:
            return HttpResponse(status=404)


# order详细
def order_details(request, order_id):
    order = Order.objects.filter(id=order_id)
    if order:
        item_list = json.loads(order[0].details)
        return render(request, 'order.html', {'order': order[0], 'item_list': item_list})
    else:
        return HttpResponse(status=404)


# order 操作
@login_required()
def order_operation(request, order_id, option):
    # status定义和option定义分别见model.Order和my_order.html
    if request.method == 'GET':
        order = Order.objects.filter(id=order_id)
        if order:
            order = order[0]
            user, user_type = get_user_type(request.user)
            try:
                option = int(option)
            except ValueError:
                return HttpResponse(404)
            if user_type == 'buyer':
                if order.buyer == user:
                    if order.status == 0 and option == 1:   # 创建订单后取消付款
                        order.last_status = order.status
                        order.status = 5
                        order.save()
                        return redirect(reverse('account:MyOrders'))
                    elif option == 2 and (order.status == 1 or order.status == 2 or order.status == 3):     # 付款后申请退款
                        order.last_status = order.status
                        order.status = 4
                        order.save()
                        return redirect(reverse('account:MyOrders'))
                    elif order.status == 4 and option == 3:     # 申请退款时取消申请退款
                        last_status = order.last_status
                        order.status = order.last_status
                        order.last_status = last_status
                        order.save()
                        return redirect(reverse('account:MyOrders'))
                    elif order.status == 2 and option == 5:     # 发货后确认收货
                        order.last_status = order.status
                        order.status = 3
                        order.finished = True
                        order.save()
                        order.shop.owner.balance += order.total_amount
                        order.shop.owner.save()
                        details = json.loads(order.details)
                        for item in details:
                            if not BuyerAndItem.objects.filter(item__item_id= item['item_id']):
                                BuyerAndItem(buyer=order.buyer,
                                             item=Item.objects.filter(item_id=item['item_id'],
                                                                      version=item['version'])[0]).save()
                        return redirect(reverse('account:MyOrders'))
                    elif order.status == 6 and option == 4:
                        order.status = order.last_status
                        order.last_status = 6
                        order.save()
                        return redirect(reverse('account:MyOrders'))
                # 如果都不行
                return HttpResponse(status=403)
            elif user_type == 'seller':
                if order.shop.owner == user:
                    if order.status == 1 and option == 6:
                        order.last_status = order.status
                        order.status = 2
                        order.save()
                        return redirect(reverse('account:MyOrders'))
                    elif order.status == 4 and option == 7:
                        if order.last_status == 1:
                            order.status = 5
                            order.save()
                            order.buyer.balance += order.total_amount
                            order.buyer.save()
                            return redirect(reverse('account:MyOrders'))
                        else:
                            order.status = 6
                            order.save()
                            return redirect(reverse('account:MyOrders'))
                    elif order.status == 4 and option == 8:
                        print(order.last_status)
                        last_status = order.last_status
                        order.status = order.last_status
                        order.last_status = last_status
                        order.save()
                        return redirect(reverse('account:MyOrders'))
                    elif order.status == 6 and option == 9:
                        order.last_status = order.status
                        order.status = 5
                        order.save()
                        order.buyer.balance += order.total_amount
                        order.buyer.save()
                        if order.finished:
                            order.shop.owner.balance -= order.total_amount
                            order.shop.owner.save()
                        return redirect(reverse('account:MyOrders'))
                return HttpResponse(status=403)
            else:
                return HttpResponse(status=403)
    else:
        return HttpResponse(status=404)
