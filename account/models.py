from django.db import models
from django.contrib.auth.models import User
from .classes import WebUser

# Create your models here.


class UserSeller(models.Model, WebUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User', primary_key=True)
    user_type = models.IntegerField(choices=((0, '买家'), (1, '卖家')))

    def web_user_is_extended_to_model(self):
        pass


class UserBuyer(models.Model, WebUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User', primary_key=True)
    user_type = models.IntegerField(choices=((0, '买家'), (1, '卖家')))

    def web_user_is_extended_to_model(self):
        pass
