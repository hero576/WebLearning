from django.contrib import admin
from tt_goods.models import *
from celery_tasks.tasks import generate_index
from django.core.cache import cache

# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        #生成首页静态页面
        generate_index.delay()
        #缓存失效
        cache.delete("index")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        generate_index.delay()
        cache.delete("index")

class IndexPromotionBannerAdmin(BaseAdmin):
    list_display = ['id','name','url','index']
class GoodsCategoryAdmin(BaseAdmin):
    pass
class IndexGoodsBannerAdmin(BaseAdmin):
    pass
class IndexCategoryGoodsBannerAdmin(BaseAdmin):
    pass




admin.site.register(GoodsCategory,GoodsCategoryAdmin)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexGoodsBanner,IndexGoodsBannerAdmin)
admin.site.register(IndexCategoryGoodsBanner,IndexCategoryGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner,IndexPromotionBannerAdmin)





