import json

from django.views.decorators.http import require_POST
from django import http
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.contrib import auth

from scipio import models, forms, signals
from scipio.utils import mimeparse

def _post_redirect(request):
    return request.POST.get('redirect', request.META.get('HTTP_REFERER', '/'))

def login(request):
    """
    Shows and processes an OpenID login form. The successful response from the
    view is a redirect to user's OpenID server. The server will then return the
    user back to `complete` view.

    Requires a template "scipio/login.html".
    """
    if request.method == 'POST':
        form = forms.AuthForm(request.session, request.POST)
        if form.is_valid():
            after_auth_redirect = form.auth_redirect(request, _post_redirect(request), {'op': 'login'})
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
    """
    Completes authentication process after user returns from the OpenID server.

    If authentication is successful sends a signal about it which an
    application can catch and return some HttpResponse. If no HttpResponse
    returned from signal handlers the view just redirect a user to the original
    page from which authentication had started.
    """
    user = auth.authenticate(request=request, query=request.GET)

    if not user:
        return http.HttpResponseForbidden(message)

    data = dict((str(k[7:]), v) for k, v in request.GET.items() if k.startswith('scipio.'))
    results = signals.authenticated.send(request, user=user, **data)

    for callback, result in results:
        if isinstance(result, http.HttpResponse):
            response = result
            break
    else:
        response = redirect(request.GET.get('redirect', '/'))

    return response

def complete_login(sender, user, op=None, **kwargs):
    """
    A default handler for login completion that actually athenticates a Django
    user and persists it in a session.
    """
    if op == 'login':
        auth.login(sender, user)
signals.authenticated.connect(complete_login)

@require_POST
def logout(request):
    """
    Processes logout form by logging out Django user.
    """
    auth.logout(request)
    return redirect(_post_redirect(request))

def openid_whitelist(request):
    """
    Shows current list of white-listed users to share it with whoever wants to
    know users trusted by this site.

    The list is available in three formats (text, xml, json). The format is
    negotiated by HTTP spec using Accept header.
    """
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
            json.dump(list(openids), response)
            return response
        if mimetype == 'text/plain':
            return http.HttpResponse((o + '\n' for o in openids), mimetype=mimetype)
        return http.HttpResponse('Can accept only: %s' % ', '.join(MIMETYPES), status=406)
