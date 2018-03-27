from django.shortcuts import render, HttpResponse
from .models import *


# Create your views here.

def test(request):
    goodscat = GoodsCategory.objects.get(pk=3)
    context = {
        "goodscat": goodscat
    }
    return render(request, "goods_image_test.html", context)


def index(request):
    category_list = GoodsCategory.objects.all()
    banner_list = IndexGoodsBanner.objects.all().order_by("index")
    adv_list = IndexPromotionBanner.objects.all().order_by("index")

    for category in category_list:
        category.title_list = IndexCategoryGoodsBanner.objects.filter(category=category,display_type=0).order_by("index")[0:3]
        category.image_list = IndexCategoryGoodsBanner.objects.filter(category=category,display_type=1).order_by("index")[0:4]
    context = {
        "title": "首页",
        "category_list":category_list,
        "banner_list":banner_list,
        "adv_list":adv_list,
    }
    return render(request, "index.html", context)
