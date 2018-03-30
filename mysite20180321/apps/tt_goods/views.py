from django.shortcuts import render, HttpResponse, Http404
from .models import *
from django.conf import settings
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.paginator import Paginator,Page

# Create your views here.

def test(request):
    goodscat = GoodsCategory.objects.get(pk=3)
    context = {
        "goodscat": goodscat
    }
    return render(request, "goods_image_test.html", context)


def index(request):
    # 获取缓存
    context = cache.get("index")
    if context == None:

        category_list = GoodsCategory.objects.all()
        banner_list = IndexGoodsBanner.objects.all().order_by("index")
        adv_list = IndexPromotionBanner.objects.all().order_by("index")

        for category in category_list:
            category.title_list = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=0).order_by(
                "index")[0:3]
            category.image_list = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=1).order_by(
                "index")[0:4]
        context = {
            "title": "首页",
            "category_list": category_list,
            "banner_list": banner_list,
            "adv_list": adv_list,
        }
        # 加入缓存
        cache.set('index', context, 3600)

    response = render(request, "index.html", context)
    # with open(settings.GENERATE_DIRS+"index.html", 'w') as f:
    #     f.write(response.content.decode())
    return response


def detail(request, sku_id):
    try:
        sku = GoodsSKU.objects.get(pk=sku_id)
    except:
        raise Http404()
    # 查询分类
    category_list = GoodsCategory.objects.all()

    # 查询同类商品最新的两个商品

    # 方法一：通过GoodsSKU
    new_list = GoodsSKU.objects.filter(category_id=sku.category_id).order_by("-id")[0:2]
    # new_list=GoodsSKU.objects.filter(category_id=sku.category.id).order_by("-id")[0:2]
    # new_list=GoodsSKU.objects.filter(category=sku.category).order_by("-id")[0:2]

    # 方法二（错误的）：不能通过GoodsCategory.objects.filter，返回的是一个通过GoodsCategory查询的数据集，获得的不是sku的信息，而是商品类别信息。
    # new_list=GoodsCategory.objects.get(goodsku_set=sku).goodssku_set.all().order_by("-id")[0:2]

    # 方法三：通过sku对象
    # new_list=sku.category.goodssku_set.all().order_by("-id")[0:2]

    # 陈列其他商品信息
    other_list = sku.goods.goodssku_set.all()

    # 保存用户最近浏览商品信息
    if request.user.is_authenticated:
        client = get_redis_connection()
        # 数据库已经存在
        client.lrem('history%d' % request.user.id, 0, sku_id)
        client.lpush('history%d' % request.user.id, sku_id)

        # 大于5个
        if client.llen('history%d' % request.user.id) > 5:
            client.rpop('history%d' % request.user.id)

    context = {
        "title": "商品详情",
        "sku": sku,
        'category_list': category_list,
        'new_list': new_list,
        'other_list': other_list,
    }
    return render(request, "detail.html", context)


def list_sku(request, category_id):
    # 商品列表页面，展示同一类别的所有商品

    pindex=int(request.GET.get("pindex",1))
    i_order=int(request.GET.get("order",1))

    try:
        category = GoodsCategory.objects.get(pk=category_id)
    except:
        raise Http404()
    # 查询此分类所有商品
    #oder=1,2,3,4：最新、价格降、价格升、人气
    if i_order==2:
        sku_list = GoodsSKU.objects.filter(category=category).order_by("-price")
    elif i_order==3:
        sku_list = GoodsSKU.objects.filter(category=category).order_by("price")
    elif i_order==4:
        sku_list = GoodsSKU.objects.filter(category=category).order_by("-sales")
    else:
        sku_list = GoodsSKU.objects.filter(category=category).order_by("-id")


    # 查询此分类下的所有商品，并推荐最新的两个sku
    # suggest_list = GoodsSKU.objects.filter(category=category).order_by("-id")[0:2]
    suggest_list = category.goodssku_set.all().order_by("-id")[0:2]

    #实现分页
    paginator=Paginator(sku_list,5)
    p_total=paginator.num_pages

    if pindex<1:
        pindex=1
    elif pindex>p_total:
        pindex=p_total
    p=paginator.page(pindex)

    if p_total<5:
        plist=range(1,p_total+1)
    else:
        if pindex<=2:
            plist = range(1, 6)
        elif pindex>=p_total-1:
            plist = range(p_total-4, p_total+1)
        else:
            plist = range(pindex-2, pindex+3)

    context = {
        "title": "商品列表",
        "cate": category,
        'suggest_list':suggest_list,
        'p':p,
        'order':i_order,
        'plist':plist,
    }
    return render(request, "list.html", context)
