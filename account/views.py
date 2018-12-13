from django.shortcuts import render, redirect, reverse
from .forms import RegisterForm, LoginForm
from .models import UserSeller, UserBuyer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from shop.models import ActiveShop, Order, ActiveItem, OrderShopList
from .ValidCode import create_valid_code,verify_valid_code


# 注册函数
def register(request):
    if request.method == 'GET':
        # 构建验证码
        hashed_valid_code_url = create_valid_code()
        return render(request, 'register.html', {'form': RegisterForm(), 'valid_code': hashed_valid_code_url})
    if request.method == 'POST':
        if verify_valid_code(request.POST.get('valid_str')):
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


# 卖家中心
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


# 买家中心
@login_required()
def buyer_home(request):
    buyer = UserBuyer.objects.filter(user=request.user)
    if buyer:
        buyer = buyer[0]
        return render(request, 'buyer_home.html', {'buyer_model': buyer})


# 我的商品页面
@login_required()
def my_items(request):
    seller = UserSeller.objects.filter(user=request.user)
    if seller:
        seller = seller[0]
        item_list = ActiveItem.objects.filter(item__owner=seller)
        return render(request, 'my_items.html', {'item_list': item_list})


# 状态栏渲染 返回状态栏的HTML
def get_login_status(request):
    if request.user.is_authenticated:
        status_bar = r"欢迎，" + request.user.username + '！' \
            " <a href=\"/\">主页</a>" \
            " <a href=\"/account/{0}\">个人中心</a>"
        user = UserSeller.objects.filter(user=request.user)
        if user:
            status_bar.format('seller/home')
        else:
            status_bar.format('buyer/home')
            status_bar += "<a href=\"/shop/cart\">购物车</a>"
        status_bar += "<a href=\"/account/logout\">退出登陆</a>"
    else:
        status_bar = "欢迎！ <a href=\"/\">主页</a> <a href=\"/account/register\">注册</a> <a href=\"/account/login\">登陆</a>"
    return status_bar


# 获取用户类型    参数为User类型
def get_user_type(user):
    seller = UserSeller.objects.filter(user=user)
    if seller:
        seller = seller[0]
        return seller, 1
    else:
        return UserBuyer.objects.get(user=user), 0
