# -*- coding:utf-8 -*-
from django import forms
from django.core.urlresolvers import reverse
from django.conf import settings

from scipio import authentication, utils

class AuthForm(forms.Form):
    openid_url = forms.CharField(label='OpenID', max_length=200, required=True)

    def __init__(self, session, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.session = session

    def clean_openid_url(self):
        url = self.cleaned_data['openid_url'].strip()
        try:
            self.request = authentication.create_request(url, self.session)
        except authentication.OpenIdError, e:
            raise ValidationError(e)
        return url

    def auth_redirect(self, target, data={}):
        trust_url = settings.SCIPIO_TRUST_URL or utils.absolute_url('/')
        return_to = utils.absolute_url(reverse('scipio.views.complete'))
        self.request.return_to_args['redirect'] = target
        data = dict(('scipio.%s' % k, v) for k, v in data.items())
        self.request.return_to_args.update(data)
        return self.request.redirectURL(trust_url, return_to)
