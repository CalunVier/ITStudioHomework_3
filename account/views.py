from django.shortcuts import render, redirect, reverse
from .forms import RegisterForm, LoginForm, ChangePasswordForm
from .models import UserSeller, UserBuyer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from shop.models import ActiveShop, Order, ActiveItem, OrderShopList
from .ValidCode import create_valid_code,verify_valid_code

valid_code_data = {}


# 注册函数
def register(request):
    def get_reg_render(form=None, message=''):
        hash_valid_str, data = create_valid_code()
        valid_code_data[hash_valid_str] = data
        response = render(request, 'register.html',
                          {'form': RegisterForm(form), 'message': message, 'valid_code': hash_valid_str})
        response.set_cookie(key='valid_code', value=hash_valid_str)
        return response

    if request.method == 'GET':
        # 构建验证码
        # hash_valid_str, data = create_valid_code()
        # valid_code_data[hash_valid_str] = data
        # response = render(request, 'register.html', {'form': RegisterForm(), 'valid_code': hash_valid_str})
        # response.set_cookie(key='valid_code', value=hash_valid_str)
        return get_reg_render()
    elif request.method == 'POST':
        if verify_valid_code(request.POST.get('valid_str'), request.COOKIES.get('valid_code')):
            form = RegisterForm(request.POST)
            if form.is_valid():
                def set_user():
                    # 注册用户
                    user = User.objects.create_user(form.cleaned_data['username'],     # UserName
                                                    form.cleaned_data['email'],        # Email
                                                    form.cleaned_data['password'],     # Password
                                                    )                                  # Has already been saved
                    # User写入用户信息
                    user.first_name = form.cleaned_data['first_name']       # 写入名字
                    user.last_name = form.cleaned_data['last_name']         # 写入姓氏
                    user.save()                                             # 保存
                    return user
                print(form.cleaned_data['user_type'])

                # 分不同用户类型写入自定义用户信息
                if form.cleaned_data['user_type'] == '0': # 如果是买家
                    user = set_user()
                    UserBuyer(user=user, user_type=form.cleaned_data['user_type']).save()
                elif form.cleaned_data['user_type'] == '1':   # 如果是卖家
                    user = set_user()
                    UserSeller(user=user, user_type=form.cleaned_data['user_type']).save()
                else:   # 如果都不是 ？？？捣乱？？？
                    hash_valid_str, data = create_valid_code()
                    valid_code_data[hash_valid_str] = data
                    response = render(request, 'register.html',
                                      {'form': RegisterForm(), 'message': '注册失败', 'valid_code': hash_valid_str})
                    response.set_cookie(key='valid_code', value=hash_valid_str)
                    return response

                response = redirect(reverse('account:Login'))
                response.delete_cookie('valid_code')
                return response
            else:
                return get_reg_render(request.POST, '注册失败')
        else:   # 验证码错误
            return get_reg_render(request.POST, '验证码错误')
    else:
        return HttpResponse(status=404)


# 登陆函数
def login(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'login.html', {'form': LoginForm(), 'status_bar': get_status_bar(request)})
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                # print('表单验证通过')
                # print('验证用户：', form.cleaned_data['username'])
                user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password'])
                if user is not None:
                    # print('用户', form.cleaned_data['username'], '验证通过')
                    auth.login(request, user)
                    return redirect(reverse('Index'))
                else:
                    # print('用户', form.cleaned_data['username'], '验证失败')
                    return render(request, 'login.html',
                                  {'form': LoginForm(), 'message': '用户名或密码错误', 'status_bar': get_status_bar(request)})
        else:
            return HttpResponse(status=404)
    else:   # 如果登陆了
        return render(request, 'message.html', {'status_bar': get_status_bar(request),
                                                'message_title': '你已登录', 'message': '你已经登陆了，不能重复登陆',
                                                'other': '<a href="/account/logout/">退出</a>'})


# 登出函数
def logout(request):
    if request.method == 'GET':
        print('logout()')
        auth.logout(request)
        return redirect(reverse('account:Login'))


# 修改密码
@login_required()
def change_password(request):
    if request.method == 'GET':
        return render(request, 'change_password.html', {'status_bar': get_status_bar(request),
                                                        'form': ChangePasswordForm()})
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            if authenticate(username=request.user.username, password=form.cleaned_data['old_password']):
                request.user.set_password(form.cleaned_data['new_password'])
                return redirect(reverse('account:Login'))
            else:
                return render(request, 'change_password.html', {'status_bar': get_status_bar(request),
                                                                'form': ChangePasswordForm(),
                                                                'message': '原密码错误'})


# 卖家中心
@login_required()
def seller_home(request):
    seller, user_type = get_user_type(request.user)
    if user_type == 'seller':
        if request.method == 'GET':
            return render(request, 'seller_home.html')
        else:
            return HttpResponse(status=404)
    return render(request, 'message.html', {'message_title': '你不是卖家', 'massage': '你不是买家，不能访问该页面'})


# 我的订单
@login_required()
def my_orders(request):
    order_list = None
    user_type = None
    buyer = UserBuyer.objects.filter(user=request.user)
    if buyer:
        buyer = buyer[0]
        order_list = Order.objects.filter(buyer=buyer)
        user_type = 'buyer'
    else:
        seller = UserSeller.objects.filter(user=request.user)
        if seller:
            seller = seller[0]
            order_list = OrderShopList.objects.filter(shop__owner=seller)
            user_type = 'seller'

    if user_type:
        return render(request, 'my_order.html', {'order_list': order_list, 'user_type': user_type,
                                                 'status_bar':get_status_bar(request)})
    else:
        return HttpResponse(status=403)


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
def get_status_bar(request):
    if request.user.is_authenticated:   # 检查是否登陆
        status_bar = r"欢迎，" + request.user.username + '！' \
            " <a href=\"/\">主页</a>" \
            " <a href=\"/account/{0}\">个人中心</a>"
        user = UserSeller.objects.filter(user=request.user)
        if user:
            status_bar = status_bar.format('seller/home')
        else:
            status_bar = status_bar.format('buyer/home')
            status_bar += " <a href=\"/shop/cart\">购物车</a>"
        status_bar += " <a href=\"/account/logout\">退出</a><br/>"
    else:   # 没登陆时
        status_bar = "欢迎！ <a href=\"/\">主页</a> " \
                     "<a href=\"/account/register\">注册</a> " \
                     "<a href=\"/account/login\">登陆</a><br/>"
    return status_bar


# 获取用户类型    参数为User类型
def get_user_type(row_user):
    if row_user:
        buyer = UserBuyer.objects.filter(user=row_user)
        if buyer:
            return buyer[0], 'buyer'
        else:
            seller = UserSeller.objects.filter(user=row_user)
            if seller:
                return seller[0], 'seller'
    else:
        return None, None
