from django.shortcuts import render, redirect, reverse
from .forms import RegisterForm, LoginForm
from .models import UserInfo
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth


# 注册函数
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html', {'form': RegisterForm()})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 注册用户
            user = User.objects.create_user(form.cleaned_data['username'],     # UserName
                                            form.cleaned_data['email'],        # Email
                                            form.cleaned_data['password'],     # Password
                                            )                                  # Has already been saved
            # 写入用户信息
            user.first_name = form.cleaned_data['first_name']       # 写入名字
            user.last_name = form.cleaned_data['last_name']         # 写入姓氏
            user.save()                                             # 保存
            UserInfo(user=user, user_type=form.cleaned_data['user_type']).save()
            return render(request, 'register.html', {'form': RegisterForm(), 'message': '注册成功'})
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
