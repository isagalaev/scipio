# -*- coding:utf-8 -*-
import re
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
from django.contrib.sites.models import Site

def absolute_url(url):
    if url.startswith('http://') or url.startswith('https://'):
        return url
    return 'http://%s%s' % (Site.objects.get_current().domain, url)

def read_hcard(url):
    try:
        soup = BeautifulSoup(urlopen(self.openid).read(512 * 1024))
    except IOError:
        return
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
    return {
        'nickname': info['nickname'] or info['fn'],
    }
