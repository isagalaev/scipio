# -*- coding:utf-8 -*-
import re
from urllib2 import urlopen
from datetime import datetime
import md5
import urlparse

from BeautifulSoup import BeautifulSoup
from openid.extensions.sreg import SRegResponse
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode

def absolute_url(url):
    if url.startswith('http://') or url.startswith('https://'):
        return url
    return 'http://%s%s' % (Site.objects.get_current().domain, url)

def read_hcard(url):
    try:
        soup = BeautifulSoup(urlopen(url).read(512 * 1024))
    except IOError:
        return
    vcard = soup.find(None, {'class': re.compile(r'\bvcard\b')})
    if vcard is None:
        return

    def _parse_property(class_name):
        el = vcard.find(None, {'class': re.compile(r'\b%s\b' % class_name)})
        if el is None:
            return
        if el.name == u'abbr' and el.get('title'):
            result = el['title']
        else:
            result = ''.join([s for s in el.recursiveChildGenerator() if isinstance(s, unicode)])
        return result.replace('\n',' ').strip()

    return {
        'nickname': _parse_property('nickname') or _parse_property('fn') or '',
    }

def get_names(openid_info):
    '''
    Gets username and nickname from OpenID auth completion info. A username is
    meant to be unique and as nice as possible, a nickname is what a user
    explicitly recommends to use or as nice as possible.
    '''
    hcard = read_hcard(openid_info.identity_url)

    def from_sreg():
        sreg_response = SRegResponse.fromSuccessResponse(openid_info)
        if sreg_response is not None:
            return smart_unicode(sreg_response.get('nickname', sreg_response.get('fullname')))

    def from_hcard():
        return hcard and hcard.get('nickname')

    def from_url():
        schema, host, path, query, fragment = urlparse.urlsplit(openid_info.identity_url)
        if query: # it's definitely not meant to be remotely readable
            return u'%s%s?%s' % (host, path, query)
        bits = [b for b in path.split('/') if b]
        if bits:
            if len(bits[-1]) > 20: # looks like some unreadable hash
                return smart_unicode(host + path)
            return smart_unicode(bits[-1])
        bits = [b for b in host.split('.') if b]
        if len(bits) > 2:
            return smart_unicode(bits[0])

    def unique_name():
        name = u'scipio_%s' % md5.new(openid_info.identity_url + str(datetime.now())).hexdigest()
        return name[:30]

    nickname = from_sreg() or from_hcard() or from_url() or unique_name()

    username = nickname
    if len(username) > 30 or not re.match(r'^\w+$', username):
        username = unique_name()
    while User.objects.filter(username=username):
        counter = int(re.search(r'(\d+)?$', username).group(1) or '1') + 1
        username = username + str(counter)
        if len(username) > 30:
            username = unique_name()

    return username, nickname, hcard is not None
