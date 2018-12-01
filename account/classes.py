from django.db import models
import decimal, abc


class WebUser(object):
    balance = models.DecimalField()

    def balance_add(self, delta):   # balance的增减函数，防止出现负值。结束时返回Bool值表示状态，True增减成功，False增减失败
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

    @abc.abstractmethod
    def web_user_is_extended_to_model(self):     # 标记为抽象类，继承后实现
        pass
