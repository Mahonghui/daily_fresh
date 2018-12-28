from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from .models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeDisplay, Goods, GoodsSKU
from django_redis import get_redis_connection
from orders.models import OrderGoods
from django.core.paginator import Paginator
# Create your views here.


class IndexView(View):

    def get(self, request):

        types = GoodsType.objects.all()

        goods_banner = IndexGoodsBanner.objects.all().order_by('index')

        promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

        for type in types:

            image_banner = IndexTypeDisplay.objects.filter(type=type, display_type=1).order_by('index')

            title_banner = IndexTypeDisplay.objects.filter(type=type, display_type=0).order_by('index')

            type.image_banner = image_banner
            type.title_banner = title_banner

        user = request.session.get('user', None)
        cart_count = 0

        # 获取当前用户的购物车数量
        if user is not None:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)

        context = {
            'types': types,
            'goods_banner': goods_banner,
            'promotion_banner': promotion_banners,
            'cart_count': cart_count
        }

        return render(request, 'index.html', context)



class DetailView(View):

    def get(self, request, goods_id):
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))

        types = GoodsType.objects.all()

        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

        peer_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

        user = request.session.get('user', None)
        cart_count = 0

        # 获取当前用户的购物车数量
        if user is not None:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)

            # 添加历史浏览记录
            history_key = 'history_%d'%user.id
            conn.lrem(history_key, 0, goods_id)
            conn.lpush(history_key, goods_id)
            # 只保存5条最新记录
            conn.ltrim(history_key, 0, 4)

        context = {
            'sku': sku,
            'types': types,
            'sku_orders': sku_orders,
            'new_skus': new_skus,
            'peer_skus': peer_skus,
            'cart_count': cart_count
        }

        return render(request, 'detail.html', context)


# restful api
# /list/type_id/page_num?sort=
# 种类id，页码，排序方式
class ListView(View):
    def get(self, request, type_id, page_num):
        try:
            current_type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))

        sort_way = request.GET.get('sort')
        sort = 'id'
        if sort_way == 'default':
            sort = 'id'
        elif sort_way == 'price':
            sort = 'price'
        elif sort_way == 'hot':
            sort = 'sales'

        types = GoodsType.objects.all()
        skus = GoodsSKU.objects.filter(type=current_type).order_by(sort)

        paginator = Paginator(skus, 1)

        # 页码非数值
        try:
            page_num = int(page_num)
        except ValueError:
            page_num = 1

        # 超出总页数
        if page_num > paginator.num_pages:
            page_num = 1

        page = paginator.page(page_num)

        new_skus = GoodsSKU.objects.filter(type=current_type).order_by('-create_time')[:2]

        user = request.session.get('user', None)
        cart_count = 0

        # 获取当前用户的购物车数量
        if user is not None:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)


        context = {
            'type': current_type,
            'types':types,
            'page': page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort_way
        }

        return render(request, 'list.html', context)

