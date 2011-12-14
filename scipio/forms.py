# -*- coding:utf-8 -*-
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from scipio import models, authentication, utils

class AuthForm(forms.Form):
    openid_identifier = forms.CharField(label='OpenID', max_length=200, required=True)

    def __init__(self, session, *args, **kwargs):
        super(AuthForm, self).__init__(*args, **kwargs)
        self.session = session

    def clean_openid_identifier(self):
        url = self.cleaned_data['openid_identifier'].strip()
        try:
            self.request = authentication.create_request(url, self.session)
        except authentication.OpenIdError, e:
            raise forms.ValidationError(e)
        return url

    def auth_redirect(self, target, data={}):
        trust_url = settings.SCIPIO_TRUST_URL or utils.absolute_url('/')
        return_to = utils.absolute_url(reverse('scipio.views.complete'))
        self.request.return_to_args['redirect'] = target
        data = dict(('scipio.%s' % k, v) for k, v in data.items())
        self.request.return_to_args.update(data)
        return self.request.redirectURL(trust_url, return_to)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ['nickname', 'autoupdate']

    def clean_autoupdate(self):
        if self.cleaned_data['autoupdate']:
            self.ext_data = utils.read_hcard(self.instance.openid)
            if not self.ext_data:
                raise forms.ValidationError(_('No readable profile data found on %s') % self.instance.openid)
        else:
            self.ext_data = None
        return self.cleaned_data['autoupdate']

    def save(self):
        if self.cleaned_data['autoupdate']:
            self.cleaned_data.update(self.ext_data)
        return super(ProfileForm, self).save()
