# -*- coding:utf-8 -*-
import re
import md5
from urllib2 import urlopen
from datetime import datetime

from BeautifulSoup import BeautifulSoup
from openid.consumer.consumer import Consumer, SUCCESS, DiscoveryFailure
from openid.extensions.sreg import SRegRequest, SRegResponse
from openid.store.filestore import FileOpenIDStore

from django.utils.encoding import smart_str, smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings

from scipio import models, utils, signals

def _read_hcard(self, openid):
    '''
    Ищет на странице, на которую указывает openid, микроформамт hCard,
    и берет оттуда имя, если есть.
    '''
    try:
        file = urlopen(openid).read(512 * 1024)
    except IOError:
        return
    soup = BeautifulSoup(content)
    vcard = soup.find(None, {'class': re.compile(r'\bvcard\b')})
    if vcard is None:
        return

    def _parse_property(class_name):
        el = vcard.find(None, {'class': re.compile(r'\b%s\b' % class_name)})
        if el is None:
            return
        if el.name == u'abbr' and el['title']:
            result = el['title']
        else:
            result = ''.join([s for s in el.recursiveChildGenerator() if isinstance(s, unicode)])
        return result.replace('\n',' ').strip().encode(settings.DEFAULT_CHARSET)

    info = dict((n, _parse_property(n)) for n in ['nickname', 'fn'])
    return info['nickname'] or info['fn']

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
            unique = md5.new(info.identity_url + str(datetime.now())).hexdigest()[:23] # 30 - len('scipio_')
            user = User.objects.create_user('scipio_%s' % unique, 'user@cicero', User.objects.make_random_password())
            profile = models.Profile.objects.create(
                user = user,
                openid = smart_unicode(info.identity_url),
                openid_server = smart_unicode(info.endpoint.server_url),
            )
            sreg_response = SRegResponse.fromSuccessResponse(info)
            if sreg_response is not None:
                profile.nickname = smart_unicode(sreg_response.get('nickname', sreg_response.get('fullname', '')))
            if not profile.nickname:
                profile.nickname = _read_hcard(info.identity_url)
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
