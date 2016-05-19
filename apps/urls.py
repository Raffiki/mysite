from django.conf.urls import url
from apps.views import twitter_login, twitter_logout, \
    twitter_authenticated


from . import views

urlpatterns = [
    url(r'^list/$', views.list, name='list'),
    url(r'^login/?$', twitter_login),
    url(r'^logout/?$', twitter_logout),
    url(r'^login/authenticated/?$', twitter_authenticated),
    url(r'^$', views.index, name='index'),
]