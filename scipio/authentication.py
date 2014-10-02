# -*- coding:utf-8 -*-
from openid.consumer import Consumer, AuthenticationError
from openid.extensions.sreg import SRegRequest
from openid.store.filestore import FileOpenIDStore
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings

from scipio import models, utils


class OpenIdBackend(object):
    def authenticate(self, request=None, query=None):
        consumer = get_consumer(request.session)
        try:
            info = consumer.complete(query, utils.absolute_url(request, request.path))
            profile = models.Profile.objects.from_openid(info)
            return profile.user
        except AuthenticationError:
            pass

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class OpenIdSetupError(Exception):
    pass

class OpenIdError(Exception):
    pass

def get_consumer(session):
    if not settings.SCIPIO_STORE_ROOT:
        raise OpenIdSetupError('SCIPIO_STORE_ROOT is not set')
    return Consumer(session, FileOpenIDStore(settings.SCIPIO_STORE_ROOT))

def create_request(openid_url, session):
    errors = []
    try:
        consumer = get_consumer(session)
        request = consumer.begin(openid_url)
        if request is None:
            errors.append(_('OpenID service is not found'))
    except Exception as e:
        errors.append(str(e))
    if errors:
        raise OpenIdError(errors)
    sreg_request = SRegRequest(optional=['nickname', 'fullname'])
    request.addExtension(sreg_request)
    return request
