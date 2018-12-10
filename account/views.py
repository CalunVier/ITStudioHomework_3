from django.shortcuts import render, redirect, reverse
from .forms import RegisterForm, LoginForm
from .models import UserSeller, UserBuyer, Cart
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from shop.models import ActiveShop, Order, ActiveItem, OrderShopList
from .ValidCode import ValidCodeImg

# 注册函数
def register(request):
    if request.method == 'GET':
        # img = ValidCodeImg()
        # data, valid_str = img.getValidCodeImg()
        # valid_str = hash(valid_str)
        # f = open('/static/valid_code/'+str(valid_str), 'wb')
        # f.write(data)
        return render(request, 'register.html', {'form': RegisterForm()})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 注册用户
            user = User.objects.create_user(form.cleaned_data['username'],     # UserName
                                            form.cleaned_data['email'],        # Email
                                            form.cleaned_data['password'],     # Password
                                            )                                  # Has already been saved
            # User写入用户信息
            user.first_name = form.cleaned_data['first_name']       # 写入名字
            user.last_name = form.cleaned_data['last_name']         # 写入姓氏
            user.save()                                             # 保存
            # 写入自定义用户信息
            # 分不同用户类型写入
            if form.cleaned_data['user_type']:
                UserSeller(user=user, user_type=form.cleaned_data['user_type']).save()
            else:
                UserBuyer(user=user, user_type=form.cleaned_data['user_type']).save()

            return redirect(reverse('account:Login'))
        return render(request, 'register.html', {'form': RegisterForm(form), 'message': '注册失败'})


# 登陆函数
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': LoginForm()})
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            print('表单验证通过')
            print('验证用户：', form.cleaned_data['username'])
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                print('用户', form.cleaned_data['username'], '验证通过')
                auth.login(request, user)
                return render(request, 'login.html', {'form': LoginForm(), 'message': '登陆成功'})
            else:
                print('用户', form.cleaned_data['username'], '验证失败')
        return render(request, 'login.html', {'form': LoginForm(), 'message': '失败'})


# 登出函数
def logout(request):
    if request.method == 'GET':
        print('logout()')
        auth.logout(request)
        return redirect(reverse('account:Login'))


@login_required()
def seller_home(request):
    seller = UserSeller.objects.filter(user=request.user)
    if seller:
        seller = seller[0]
        return render(request, 'seller_home.html', {'seller_model': seller})


# 我的订单
@login_required()
def my_orders(request):
    order_list = None
    buyer = UserBuyer.objects.filter(user=request.user)
    if buyer:
        buyer = buyer[0]
        order_list = Order.objects.filter(buyer=buyer)

    seller = UserSeller.objects.filter(user=request.user)
    if seller:
        seller = seller[0]
        order_list = Order.objects.filter(seller=seller)
    return render(request, 'my_order.html', {'order_list': order_list})


# 我的店铺 Seller
@login_required()
def my_mall(request):
    seller = UserSeller.objects.filter(user=request.user)
    if seller:
        seller = seller[0]
        shop_list = ActiveShop.objects.filter(shop__owner=seller)
        return render(request, 'seller_myshop.html', {'shop_list': shop_list})


@login_required()
def buyer_home(request):
    buyer = UserBuyer.objects.filter(user=request.user)
    if buyer:
        buyer = buyer[0]
        return render(request, 'buyer_home.html', {'buyer_model': buyer})


@login_required()
def buyer_cart(request):
    buyer = UserBuyer.objects.filter(user=request.user)
    if buyer:
        buyer = buyer[0]
        cart_item_list = Cart.objects.filter(buyer=buyer)
        # for 检查购物车中的Item是否为active，同时尝试替换为最新版本
        for cart_item in cart_item_list:
            if not cart_item.item.active:
                active_item_queryset = ActiveItem.objects.filter(id=cart_item.item.id)
                if active_item_queryset:
                    cart_item.item = active_item_queryset[0].item
        cart_item_list.update()

        return render(request, 'buyer_cart.html', {'cart_item_list': cart_item_list})

@login_required()
def my_items(request):
    seller = UserSeller.objects.filter(user=request.user)
    if seller:
        seller = seller[0]
        item_list = ActiveItem.objects.filter(item__owner=seller)
        return render(request, 'my_items.html', {'item_list': item_list})


# def get_login_status(request):


