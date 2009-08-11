# -*- coding:utf-8 -*-
from scipio import models

class WhitelistHandler(object):
    def _profile_in_whitelist(self, profile):
        try:
            models.CleanOpenID.objects.get(openid=profile.openid)
            return True
        except CleanOpenID.DoesNotExist:
            return False

    def validate(self, request):
        try:
            profile = request.user.scipio_profile
        except models.Profile.DoesNotExist:
            return
        if profile.spamer == True:
            return 'spam'
        elif profile.spamer == False or \
             models.CleanOpenID.objects.filter(openid=profile.openid):
            return 'clean'

class HoneyPotHandler(object):
    def __init__(self, fieldnames=['email']):
        self.fieldnames = fieldnames

    def validate(self, request):
        values = [request.POST.get(f) for f in self.fieldnames]
        if [v for v in values if v]:
            return 'spam'

class Conveyor(object):
    def __init__(self, handlers=None):
        if handlers is None:
            handlers = [
                WhitelistHandler(),
                HoneyPotHandler(),
            ]
        self.handlers = handlers

    def validate(self, request):
        status = None
        for handler in self.handelrs:
            result = handlers.validate(request)
            if result in ['clean', 'spam']:
                return result
            if result is not None:
                status = result
        return status or 'clean'

    def submit(self, kind, spam_status, request):
        for handler in self.handlers:
            func = getattr(handler, 'submit_%s' % kind, None)
            if func:
                func(spam_status, request)
