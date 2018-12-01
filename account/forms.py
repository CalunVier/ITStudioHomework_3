from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=16, min_length=3, label='用户名')
    password = forms.CharField(max_length=16, min_length=3, label='密码', widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=16, min_length=3, label='确认密码', widget=forms.PasswordInput)
    email = forms.EmailField(label='电子邮箱')
    last_name = forms.CharField(max_length=10, min_length=1, label='姓氏')
    first_name = forms.CharField(max_length=10, min_length=1, label='名字')
    user_type = forms.ChoiceField(((0, '买家'), (1, '卖家')), label='用户类型')


class LoginForm(forms.Form):
    username = forms.CharField(max_length=16, min_length=3, label='用户名')
    password = forms.CharField(max_length=16, min_length=3, label='密码', widget=forms.PasswordInput)
