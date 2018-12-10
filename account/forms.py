from django import forms
from django.contrib.auth.models import User
import re


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100, min_length=3, label='用户名',
                               error_messages={'required': '请输入账号',
                                               'max_length': "用户名长度不能大于100",
                                               'min_length': "用户名长度必须大于3"})
    password = forms.CharField(max_length=16, min_length=3, label='密码', widget=forms.PasswordInput,
                               error_messages={'required': "请输入密码",
                                               'max_length': "密码长度不能大于16",
                                               'min_length': "密码长度必须大于3"})
    confirm_password = forms.CharField(max_length=16, min_length=3, label='确认密码', widget=forms.PasswordInput,
                                       error_messages={'required': "请输入密码",
                                                       'max_length': "密码长度不能大于16",
                                                       'min_length': "密码长度必须大于3"})
    email = forms.EmailField(label='电子邮箱')
    last_name = forms.CharField(max_length=10, min_length=1, label='姓氏')
    first_name = forms.CharField(max_length=10, min_length=1, label='名字')
    user_type = forms.ChoiceField(((0, '买家'), (1, '卖家')), label='用户类型')

    def clean_username(self):
        row_username = self.cleaned_data['username']
        if re.search(r'\W', row_username):
            raise forms.ValidationError("用户名只能包含字母、数字和下划线")
        if User.objects.filter(username=row_username):
            raise forms.ValidationError("用户名已被注册")
        return row_username

    def clean_password(self):
        row_password = self.cleaned_data['password']
        if re.search(r'[^A-Za-z0-9_:.`~]', row_password):
            raise forms.ValidationError("密码只能包含字母、数字和_:.`~")
        return row_password

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        row_confirm_password = self.cleaned_data['confirm_password']
        if password != row_confirm_password:
            raise forms.ValidationError("两次输入的密码不一致")
        return row_confirm_password


class LoginForm(forms.Form):
    username = forms.CharField(max_length=16, min_length=3, label='用户名')
    password = forms.CharField(max_length=16, min_length=3, label='密码', widget=forms.PasswordInput)
