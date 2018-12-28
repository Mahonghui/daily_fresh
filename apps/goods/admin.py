from django.contrib import admin
# from celery_tasks.tasks import generate_static_index

from .models import GoodsType, IndexPromotionBanner, IndexTypeDisplay, IndexGoodsBanner, GoodsSKU, Goods,GoodsImage
# Register your models here.


# class BaseAdminModel(admin.ModelAdmin):
#     '''修改后台管理的行为'''
#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#
#         # 修改行为发生后，通知celery生成新的静态页面
#         generate_static_index.delay()
#
#     def delete_model(self, request, obj):
#         super().delete_model(request, obj)
#
#         generate_static_index.delay()


# class GoodsTypeAdmih(BaseAdminModel):
#     pass
#
#
# class IndexPromotionBannerAdmin(BaseAdminModel):
#     pass
#
#
# class IndexTypeDisplayAdmin(BaseAdminModel):
#     pass
#
#
# class IndexGoodsBannerAdmin(BaseAdminModel):
#     pass
#

admin.site.register(GoodsType)
admin.site.register(IndexPromotionBanner)
admin.site.register(IndexTypeDisplay)
admin.site.register(IndexGoodsBanner)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)