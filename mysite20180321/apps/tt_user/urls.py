from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'register',RegisterView.as_view() ),
    url(r'exists', exists),
    url(r'active/(.+)', active),
    url(r'login', LoginView.as_view()),
    url(r'logout', userlogout),
    url(r'info', info),
    url(r'order', order),
    url(r'addr', SiteView.as_view()),
    url(r'addarea', addarea),

]
