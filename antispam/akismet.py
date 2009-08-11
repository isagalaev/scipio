from urllib2 import urlopen, Request

from django.utils.http import urlencode
from django.conf import settings

def _base_data(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '') or \
         request.META.get('REMOTE_ADDR', '')
    ip = ip.split(',')[0].strip()
    return {
        'user_ip': ip,
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERER', ''),
        'HTTP_ACCEPT': request.META.get('HTTP_ACCEPT', ''),
    }

def _post(op, request, index_url, **kwargs):
    url = 'http://%s.rest.akismet.com/1.1/%s' % (
        settings.SCIPIO_AKISMET_KEY,
        op # comment-check, submit-spam, submit-ham
    )
    data = dict(_base_data(request), blog=index_url)
    data.update(kwargs)
    response = urlopen(Request(url,
        urlencode(data),
        {
            'Content-type': 'application/x-www-form-urlencoded',
            'User-agent': 'Scipio/0.1',
        }
    )).read()
    if response == 'true':
        return True
    elif response == 'false':
        return False
    elif response == 'invalid':
        raise Exception('Invalid Akismet key')
    else:
        raise Exception('Unknown response from Akismet: %s' % response)

class AkismetHandler(object):
    def __init__(self, param_func=lambda r: {}):
        self.param_func = param_func

    def validate(self, request):
        if _post('comment-check', request, **self.param_func(request)):
            return 'akismet'

    def submit_spam(self, spam_status, request):
        _post('submit-spam', request, **self.param_func(request))

    def submit_ham(self, spam_status, request):
        if spam_status == 'akismet':
            _post('submit-ham', request, **self.param_func(request))
