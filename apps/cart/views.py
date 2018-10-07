from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection
# Create your views here.




class CartInfoView(View):

    def get(self, request):
        user = request.session.get('user')
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        cart_dict = conn.hgetall(cart_key)

        skus = []
        total_amount = 0
        total_price = 0
        for sku_id, count in cart_dict.items():
            sku = GoodsSKU.objects.get(id=sku_id)
            sku_price = sku.price * int(count)

            sku.sku_price = sku_price
            sku.sku_count = count.decode()
            total_amount += int(count)
            total_price += sku_price
            skus.append(sku)

        context = {
            'skus': skus,
            'total_amount': total_amount,
            'total_price': total_price
        }

        return render(request, 'cart.html', context)

# /cart/add 接受商品id和数量
class AddCartView(View):
    '''添加购物车'''

    def post(self, request):

        user = request.session.get('user', None)

        if not user:
            return JsonResponse({'status': -1, 'errmsg': '请先登录'})

        sku_id = request.POST.get('sku_id')
        amount = request.POST.get('amount')

        # 数据校验
        if not all([sku_id, amount]):
            return JsonResponse({'status': 0, 'errmsg': '数据不完整'})

        try:
            amount = int(amount)
        except ValueError:
            return JsonResponse({'status': 0, 'errmsg': '商品信息不合法'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'status': 0, 'errmsg': '商品不存在'})

        # 写入数据库
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        # 检查商品是否已存在
        cart_res = conn.hget(cart_key, sku_id)
        if cart_res:
            amount += int(cart_res)

        if amount > sku.stock:
            return JsonResponse({'status': 0, 'errmsg': '库存不足'})
        # hset：已存在更新，不存在添加
        conn.hset(cart_key, sku_id, amount)

        totoal_count = conn.hlen(cart_key)
        return JsonResponse({'status': 1, 'total_count': totoal_count, 'errmsg': '添加成功'})

class UpdateCartView(View):
    def post(self, request):

        user = request.session.get('user', None)

        if not user:
            return JsonResponse({'status': -1, 'errmsg': '请先登录'})

        sku_id = request.POST.get('sku_id')
        amount = request.POST.get('amount')
        # 数据校验
        if not all([sku_id, amount]):
            return JsonResponse({'status': 0, 'errmsg': '数据不完整'})

        try:
            amount = int(amount)
        except ValueError:
            return JsonResponse({'status': 0, 'errmsg': '商品信息不合法'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'status': 0, 'errmsg': '商品不存在'})

        if amount > sku.stock:
            return JsonResponse({'status': 0, 'errmsg': '库存不足'})

        # 写入数据库
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        conn.hset(cart_key, sku_id, amount)

        val_list = conn.hvals(cart_key)
        sumds = sum([int(v) for v in val_list])
        return JsonResponse({'status': 1, 'sum': sumds, 'msg': '更新成功'})

class DeleteCartView(View):
    def post(self, request):

        user = request.session.get('user', None)
        if not user:
            return JsonResponse({'status': -1, 'errmsg': '请先登录'})

        sku_id = request.POST.get('sku_id')

        if not sku_id:
            return JsonResponse({'status': 0, 'errmsg': '商品信息不完整'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'status': 0, 'errmsg': '商品不存在'})

        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        conn.hdel(cart_key, sku_id)

        val_list = conn.hvals(cart_key)
        sumds = sum([int(v) for v in val_list])
        return JsonResponse({'status': 1, 'sum': sumds, 'msg':'删除成功'})