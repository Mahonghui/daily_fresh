from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.generic import View
from django.db import transaction
from django_redis import get_redis_connection
from goods.models import GoodsSKU
from .models import OrderInfo, OrderGoods
from users.models import Address
import datetime

# Create your views here.

class PlaceOrderView(View):
    def post(self, request):

        user = request.session.get('user')
        sku_ids = request.POST.getlist('sku_id')

        if not sku_ids:
            return redirect(reverse('cart:cart'))

        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        total_count = 0
        total_price = 0
        skus = []

        for sku_id in sku_ids:
            # 获取商品信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取购车中该商品的数量
            sku.amount = int(conn.hget(cart_key, sku_id))
            sku.good_sum = sku.amount * sku.price
            # 累加总金额和总数量
            total_count += sku.amount
            total_price += (sku.amount * sku.price)
            # 追加到要返回的列表
            skus.append(sku)

        # 运费，暂时硬编码
        express_fee = 8

        total_bill = total_price + express_fee
        # 地址相关
        address_list = Address.objects.filter(user=user)

        sku_ids = ','.join(sku_ids)
        context = {
            'skus': skus,
            'address_list': address_list,
            'express_fee': express_fee,
            'total_price': total_price,
            'total_count': total_count,
            'total_bill': total_bill,
            'sku_ids': sku_ids
        }
        return render(request, 'place_order.html', context)


class HandleOrderView(View):
    # 将数据库操作事务化, 防止写入无效订单
    @transaction.atomic
    def post(self, request):

        user = request.session.get('user')
        if not user:
            return JsonResponse({'status': 0, 'errmsg': '用户未登录'})

        sku_ids = request.POST.get('sku_ids').split(',')
        pay_method = request.POST.get('pay_method')
        address_id = request.POST.get('address_id')

        if not all([sku_ids, pay_method, address_id]):
            return JsonResponse({'status': 0, 'errmsg': '数据不完整'})

        address = Address.objects.get(id=address_id)

        order_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '-' + str(user.id)
        # 运费硬编码
        express_fee = 8

        # 订单的总数先用0代替，遍历完所有商品后再更新
        total_count = 0
        total_price = 0
        # 新建订单
        order = OrderInfo()
        order.order_id = order_id
        order.address = address
        order.user = user
        order.pay_method = pay_method
        order.express_fee = express_fee
        order.total_count = total_count
        order.total_price = total_price
        # 设置保存点，下方代码出错时回滚至此
        savepoint_1 = transaction.savepoint()
        order.save()
        try:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id

            for sku_id in sku_ids:
                # 新建订单的商品记录
                for i in range(3):
                    try:
                        # 悲观锁
                        # sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
                        sku = GoodsSKU.objects.get(id=sku_id)
                    except GoodsSKU.DoesNotExist:
                        return JsonResponse({'status': 0, 'errmsg': '商品不存在'})

                    # 获取购物车的对应商品数量
                    good_amount = int(conn.hget(cart_key, sku_id))
                    # 对共享的数据上锁
                    # 判断库存
                    if good_amount > sku.stock:
                        transaction.savepoint_rollback(savepoint_1)
                        return JsonResponse({'status': 0, 'errmsg': '库存不足'})
                    order_goods = OrderGoods()
                    order_goods.sku = sku
                    order_goods.order = order
                    order_goods.count = good_amount
                    order_goods.price = sku.price

                    # # 更新销量和库存
                    # sku.stock -= good_amount
                    # sku.sales += good_amount

                    # 更新库存
                    origin_stock = sku.stock
                    new_stock = origin_stock - good_amount
                    new_sales = sku.sales + good_amount
                    # 乐观锁: 判断表中数据和上次读到的是否一致
                    res = GoodsSKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                    if res == 0:
                        if i == 2:
                            transaction.savepoint_rollback(savepoint_1)
                            return JsonResponse({'status': 0, 'errmsg': '库存不足'})
                        else:
                            continue
                    order_goods.save()
                    # 保存订单信息的总价格和总数量
                    total_count += good_amount
                    total_price += (good_amount * sku.price)
                    break

            # 替换订单的总额部分
            order = OrderInfo.objects.get(order_id=order_id)
            order.total_price = total_price
            order.total_count = total_count
            order.save()
        except Exception:
            transaction.savepoint_rollback(savepoint_1)
            return JsonResponse({'status': 0, 'errmsg': '下单失败'})
        # 数据操作无误
        transaction.savepoint_commit(savepoint_1)

        # 清空购物车
        conn.hdel(cart_key, *sku_ids)
        return JsonResponse({'status': 1, 'msg': '订单创建成功'})




