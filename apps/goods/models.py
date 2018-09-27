from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField

# Create your models here.

class GoodsType(BaseModel):
    '''商品类型表'''

    name = models.CharField(max_length=20, verbose_name='类型名称')
    logo = models.CharField(max_length=20, verbose_name='类型标识')
    image = models.ImageField(upload_to='type', verbose_name='商品类型图片')

    class Meta:
        db_table = 'Goods_type'
        verbose_name = '商品种类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsSKU(BaseModel):
    '''商品SKU表'''
    STATUS_CODE = (
        (0, '下线'),
        (1, '上线')
    )

    name = models.CharField(max_length=20, verbose_name='商品名称')
    desc = models.CharField(max_length=256, verbose_name='商品简介')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    unite = models.CharField(max_length=20, verbose_name='商品单位')
    stock = models.IntegerField(default=1, verbose_name='商品库存')
    sales = models.IntegerField(default=0, verbose_name='商品销量')
    image = models.ImageField(upload_to='goods', verbose_name='商品图片')
    status = models.SmallIntegerField(choices=STATUS_CODE, default=1, verbose_name='商品是否上线')
    # 定义外键
    type = models.ForeignKey('GoodsType', verbose_name='商品种类', on_delete=models.CASCADE)
    goods = models.ForeignKey('Goods', verbose_name='商品SPU', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Goods_sku'
        verbose_name = '具体商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Goods(BaseModel):
    '''商品SPU表'''

    name = models.CharField(max_length=20, verbose_name='商品SPU名称')
    # 富文本类型
    detail = HTMLField(blank=True, verbose_name='商品详情')

    class Meta:
        db_table = 'Goods_spu'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name


class GoodsImage(BaseModel):
    '''商品图片表'''

    image = models.ImageField(upload_to='goods', verbose_name='图片路径')
    # 定义外键
    sku = models.ForeignKey('GoodsSKU', verbose_name='所属商品', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Goods_image'
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name

class IndexGoodsBanner(BaseModel):
    '''首页轮播商品表'''

    image = models.ImageField(upload_to='banner', verbose_name='图片')
    index = models.SmallIntegerField(default=0, verbose_name='轮播顺序')
    # 定义外键
    sku = models.ForeignKey('GoodsSKU', verbose_name='商品',on_delete=models.CASCADE)

    class Meta:
        db_table = 'Goods_banner'
        verbose_name = '首页轮播图片'
        verbose_name_plural = verbose_name

class IndexPromotionBanner(BaseModel):
    '''首页促销活动表'''

    name = models.CharField(max_length=20, verbose_name='活动名称')
    url = models.URLField(verbose_name='活动链接')
    image = models.ImageField(upload_to='banner', verbose_name='促销活动图片')
    index = models.SmallIntegerField(default=0, verbose_name='显示顺序')

    class Meta:
        db_table = 'Index_promotion'
        verbose_name = '首页促销'
        verbose_name_plural = verbose_name


class IndexTypeDisplay(BaseModel):
    '''首页分类展示表'''

    DISPLAY_CODE = (
        (0, '标题'),
        (1, '图片')
    )

    display_type = models.SmallIntegerField(default=0, choices=DISPLAY_CODE, verbose_name='显示类型')
    index = models.SmallIntegerField(default=0, verbose_name='显示顺序')
    # 定义外键
    sku = models.ForeignKey('GoodsSKU', verbose_name='商品SKU', on_delete=models.CASCADE)
    type = models.ForeignKey('GoodsType', verbose_name='商品类型', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Index_goods_type'
        verbose_name = '首页分类展示商品'
        verbose_name_plural = verbose_name

