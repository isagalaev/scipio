# -*- coding:utf-8 -*-
from django.views.decorators.http import require_POST
from django import http
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.contrib import auth

from scipio import models, forms, signals, mimeparse

def _post_redirect(request):
    return request.POST.get('redirect', request.META.get('HTTP_REFERER', '/'))

def login(request):
    if request.method == 'POST':
        form = forms.AuthForm(request.session, request.POST)
        if form.is_valid():
            after_auth_redirect = form.auth_redirect(_post_redirect(request), {'op': 'login'})
            return redirect(after_auth_redirect)
        return_url = _post_redirect(request)
    else:
        form = forms.AuthForm(request.session)
        return_url = request.GET.get('redirect', '/')
    return render_to_response('scipio/login.html',
        {'form': form, 'redirect': return_url},
        context_instance = RequestContext(request),
    )

def complete(request, message=_('Authentication failed')):
    user = auth.authenticate(session=request.session, query=request.GET, return_path=request.path)
    if not user:
        return http.HttpResponseForbidden(message)
    data = dict((str(k[7:]), v) for k, v in request.GET.items() if k.startswith('scipio.'))
    results = signals.authenticated.send(request, user=user, **data)
    for r in results:
        if isinstance(r, http.HttpResponse):
            response = r
            break
    else:
        response = None
    return response or redirect(request.GET.get('redirect', '/'))

def complete_login(sender, user, op=None, **kwargs):
    if op == 'login':
        auth.login(sender, user)
signals.authenticated.connect(complete_login)

@require_POST
def logout(request):
    auth.logout(request)
    return redirect(_post_redirect(request))

def openid_whitelist(request):
    if request.method == 'POST':
        try:
            profile = models.Profile.objects.get(pk=int(request.POST['id']))
            profile.spamer = False
            profile.save()
            signals.whitelist.send(sender=profile)
            return redirect(_post_redirect(request))
        except (models.Profile.DoesNotExist, ValueError, KeyError):
            return http.HttpResponseBadRequest()
    else:
        openids = (p.openid for p in models.Profile.objects.filter(spamer=False) if p.openid)
        MIMETYPES = ['application/xml', 'text/xml', 'application/json', 'text/plain']
        accept = request.META.get('HTTP_ACCEPT', '')
        try:
            mimetype = mimeparse.best_match(MIMETYPES, accept)
        except ValueError:
            mimetype = 'text/plain'
        if mimetype.endswith('/xml'):
            try:
                import xml.etree.ElementTree as ET
            except ImportError:
                import elementtree.ElementTree as ET
            root = ET.Element('whitelist')
            for openid in openids:
                ET.SubElement(root, 'openid').text = openid
            xml = ET.ElementTree(root)
            response = http.HttpResponse(mimetype=mimetype)
            xml.write(response, encoding='utf-8')
            return response
        if mimetype == 'application/json':
            response = http.HttpResponse(mimetype=mimetype)
            simplejson.dump(list(openids), response)
            return response
        if mimetype == 'text/plain':
            return http.HttpResponse((o + '\n' for o in openids), mimetype=mimetype)
        return http.HttpResponse('Can accept only: %s' % ', '.join(MIMETYPES), status=406)
