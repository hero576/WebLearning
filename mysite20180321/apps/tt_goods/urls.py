from django.conf.urls import url,include
from .views import *
import haystack.urls

urlpatterns = [
    url(r'^$', index),
    url(r'^index$', index),
    url(r'^test', test),
    url(r'^(\d+)', detail),
    url(r'^list(\d+)', list_sku),
    # url(r'^search/', include(haystack.urls)),
    url(r'^search/',MySearchView.as_view())
]
