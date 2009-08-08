# -*- coding:utf-8 -*-
from openid.consumer.consumer import Consumer, SUCCESS, DiscoveryFailure
from openid.extensions.sreg import SRegRequest
from openid.store.filestore import FileOpenIDStore
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings

from scipio import models, utils, signals

class OpenIdBackend(object):
    def authenticate(self, session=None, query=None, return_path=None):
        consumer = get_consumer(session)
        info = consumer.complete(query, utils.absolute_url(return_path))
        if info.status != SUCCESS:
            return None
        try:
            profile = models.Profile.objects.get(openid=info.identity_url)
            user = profile.user
        except models.Profile.DoesNotExist:
            username, nickname = utils.get_names(info)
            user = User.objects.create_user(username, 'user@scipio', User.objects.make_random_password())
            profile = models.Profile.objects.create(
                user = user,
                openid = smart_unicode(info.identity_url),
                openid_server = smart_unicode(info.endpoint.server_url),
                nickname = nickname,
            )
            profile.save()
            signals.created.send(sender=profile)
        return user

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
    except (DiscoveryFailure, OpenIdSetupError, ValueError), e:
        errors.append(str(e[0]))
    if errors:
        raise OpenIdError(errors)
    sreg_request = SRegRequest(optional=['nickname', 'fullname'])
    request.addExtension(sreg_request)
    return request
