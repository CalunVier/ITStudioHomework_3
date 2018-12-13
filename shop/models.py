from django.db import models
from account.models import UserSeller, UserBuyer

# Create your models here.


class Shop(models.Model):
    shop_name = models.CharField(max_length=20, verbose_name='店铺名')
    owner = models.ForeignKey(UserSeller, verbose_name='所有者')
    sales_volume = models.IntegerField(default=0, verbose_name='销售量')
    sales_amount = models.DecimalField(default=0, verbose_name='销售额', decimal_places=6, max_digits=20)
    create_time = models.DateTimeField(auto_now=True, verbose_name='创建时间')


class ActiveShop(models.Model):   # 活动的店铺
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, verbose_name='店铺')


class Item(models.Model):
    item_id = models.IntegerField(verbose_name=u'商品ID', db_index=True)
    item_name = models.CharField(max_length=60, verbose_name=u'商品名')
    version = models.IntegerField(default=0, verbose_name=u'版本号')
    owner = models.ForeignKey(UserSeller, on_delete=models.CASCADE, verbose_name=u'所有者')
    shop = models.ForeignKey(Shop, default=None, null=True, on_delete=models.CASCADE, verbose_name=u'所属店铺')
    price = models.DecimalField(default=0, verbose_name=u'商品价格', decimal_places=6, max_digits=20)
    inventory = models.IntegerField(default=0, verbose_name=u'库存')
    sales_volume = models.IntegerField(default=0, verbose_name=u'销售量')
    active = models.BooleanField(default=True, verbose_name=u'活动的')
    # introductions = models.URLField(default='', verbose_name='介绍地址')
    create_time = models.DateTimeField(auto_now=True, verbose_name=u'创建时间')
    last_edit = models.DateTimeField(auto_now_add=True, verbose_name=u'最后修改时间')

    class Meta:
        unique_together = ['item_id', 'version']


class ActiveItem(models.Model):   # 活动的商品
    item = models.OneToOneField(Item, on_delete=models.CASCADE, verbose_name=u'商品')


class PictureItem(models.Model):
    item = models.ForeignKey(ActiveItem, on_delete=models.CASCADE, verbose_name='商品')
    picture = models.URLField(verbose_name='图片')


class Order(models.Model):
    choices = ((0, '已创建'), (1, '已支付'), (2, '已发货'), (3, '已完成'), (4, '申请退货'), (5, '已关闭'))
    buyer = models.ForeignKey(UserBuyer, on_delete=models.CASCADE, verbose_name='买家')
    status = models.IntegerField(choices=choices, default=0, verbose_name='订单状态')
    create_time = models.DateTimeField(auto_now=True, verbose_name='创建时间')
    last_edit = models.DateTimeField(auto_now_add=True, verbose_name='最后修改时间')
    total_amount = models.DecimalField(default=0, verbose_name='总金额', decimal_places=6, max_digits=20)
    details = models.TextField(max_length=65535, verbose_name='订单详细')
    # details:json
    # {'item_id': cart_item.item.id,
    #  'item_name': cart_item.item.item_name,
    #  'price': cart_item.item.price,
    #  'version': cart_item.item.version}


class OrderShopList(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='商店')


class Cart(models.Model):
    user = models.ForeignKey(UserBuyer, on_delete=models.CASCADE, verbose_name='用户')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='商品')
    amount = models.IntegerField(verbose_name='数量')
    collected = models.BooleanField(default=False, verbose_name='添加到收藏')
