from django.db import models
from django.contrib.auth.models import User
import decimal
import abc
# Create your models here.


class UserSeller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User', primary_key=True)
    user_type = models.IntegerField(choices=((0, '买家'), (1, '卖家')))
    sales_amount = models.DecimalField(default=0, verbose_name='销售额', decimal_places=6, max_digits=20)
    balance = models.DecimalField(default=0, verbose_name='余额', decimal_places=6, max_digits=20)

    def balance_add(self, delta):  # balance的增减函数，防止出现负值。结束时返回Bool值表示状态，True增减成功，False增减失败
        if isinstance(delta, str):  # 如果传入str
            if (self.balance + decimal.Decimal(delta)) > 0:
                self.balance += decimal.Decimal(delta)
                self.save()
                return True
        if isinstance(delta, decimal.Decimal):  # 如果传入Decimal
            if self.balance + delta > 0:
                self.balance += delta
                self.save()
                return True
        return False


class UserBuyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User', primary_key=True)
    user_type = models.IntegerField(choices=((0, '买家'), (1, '卖家')))
    balance = models.DecimalField(verbose_name='余额', decimal_places=6, max_digits=20)

    def balance_add(self, delta):  # balance的增减函数，防止出现负值。结束时返回Bool值表示状态，True增减成功，False增减失败
        if isinstance(delta, str):  # 如果传入str
            if (self.balance + decimal.Decimal(delta)) > 0:
                self.balance += decimal.Decimal(delta)
                self.save()
                return True
        if isinstance(delta, decimal.Decimal):  # 如果传入Decimal
            if self.balance + delta > 0:
                self.balance += delta
                self.save()
                return True
        return False


class Cart(models.Model):
    buyer = models.ForeignKey(UserBuyer, on_delete=models.CASCADE, verbose_name='用户')
    item = models.ForeignKey('shop.Item', on_delete=models.CASCADE, verbose_name='商品')
    collected = models.BooleanField(default=False, verbose_name='添加到收藏')

