# -*- coding:utf-8 -*-
from django.contrib.admin import site, ModelAdmin

from scipio import models

site.register(models.Profile,
    list_display = ['user', 'openid', 'nickname', 'spamer'],
    list_filter = ['spamer'],
    search_fields = ['openid', 'nickname', 'user__username'],
)

site.register(models.WhitelistSource)

site.register(models.CleanOpenID,
    list_display = ['openid', 'source'],
    list_filter = ['source'],
)
