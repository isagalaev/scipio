from urllib2 import urlopen, Request

from django.utils.http import urlencode
from django.conf import settings

def _request_data(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '') or \
         request.META.get('REMOTE_ADDR', '')
    ip = ip.split(',')[0].strip()
    return {
        'user_ip': ip,
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERER', ''),
        'HTTP_ACCEPT': request.META.get('HTTP_ACCEPT', ''),
    }

def _post(op, request, **kwargs):
    url = 'http://%s.rest.akismet.com/1.1/%s' % (
        settings.SCIPIO_AKISMET_KEY,
        op # comment-check, submit-spam, submit-ham
    )
    data = {}
    if request is not None:
        data.update(_request_data(request))
    data.update(kwargs)
    response = urlopen(Request(url,
        urlencode(data),
        {
            'Content-type': 'application/x-www-form-urlencoded',
            'User-agent': 'Scipio/0.1',
        }
    )).read()
    if response == 'invalid':
        raise Exception('Invalid Akismet key')
    if op == 'comment-check':
        if response == 'true':
            return True
        elif response == 'false':
            return False
        else:
            raise Exception('Unknown response from Akismet: %s' % response)

class AkismetBaseHandler(object):
    def get_params(self, request, **kwargs):
        return {
            'blog': utils.absolute_url('/'),
        }

    def validate(self, request, **kwargs):
        if _post('comment-check', request, **self.get_params(request, **kwargs)):
            return 'akismet'

    def submit_spam(self, **kwargs):
        _post('submit-spam', None, **self.get_params(None, **kwargs))

    def submit_ham(self, spam_status, **kwargs):
        if spam_status == 'akismet':
            _post('submit-ham', None, **self.get_params(None, **kwargs))
