# -*- coding:utf-8 -*-
from django.conf.urls.defaults import *

from scipio import views

urlpatterns = patterns('',
    url(r'^login/$', views.login, name='scipio_login'),
    url(r'^auth/$', views.complete, name='scipio_complete'),
    url(r'^logout/$', views.logout, name='scipio_logout'),
    url(r'^openid_whitelist/$', views.openid_whitelist, name='scipio_whitelist'),
)
