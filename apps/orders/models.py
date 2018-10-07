from django.db import models
from db.base_model import BaseModel

# Create your models here.

class OrderInfo(BaseModel):
    '''订单信息表'''

    PAY_METHOD = (
        (0, '货到付款'),
        (1, '微信支付'),
        (2, '支付宝'),
        (3, '银联支付')
    )

    ORDER_STATUS = (
        (0, '待付款'),
        (1, '待发货'),
        (2, '待收货'),
        (3, '待评价'),
        (4, '已完成')
    )

    # 指定主键，默认主键不生成
    order_id = models.CharField(max_length=128, primary_key=True, verbose_name='订单ID')

    pay_method = models.SmallIntegerField(default=0, choices=PAY_METHOD, verbose_name='付款方式')
    order_status = models.SmallIntegerField(default=0, choices=ORDER_STATUS, verbose_name='订单状态')
    total_count = models.IntegerField(default=1, verbose_name='订单数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价')
    express_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')
    trade_id = models.CharField(max_length=128, default='', verbose_name='交易编号')
    # 定义外键
    user = models.ForeignKey('users.User', verbose_name='下单用户', on_delete=models.CASCADE)
    address = models.ForeignKey('users.Address', verbose_name='订单地址', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Order_info'
        verbose_name = '订单信息'
        verbose_name_plural = verbose_name

class OrderGoods(BaseModel):
    '''某个订单中的商品信息表'''

    count = models.IntegerField(default=1, verbose_name='商品数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    comment = models.CharField(max_length=256, verbose_name='商品评论', default='')
    # 定义外键
    order = models.ForeignKey('OrderInfo', verbose_name='订单', on_delete=models.CASCADE)
    sku = models.ForeignKey('goods.GoodsSKU', verbose_name='商品', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Order_goods'
        verbose_name = '订单商品信息'
        verbose_name_plural = verbose_name