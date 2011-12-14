# -*- coding:utf-8 -*-
from django import dispatch

# Successfull completion of OpenID authentication
# Parameters:
# - sender: HttpRequest instance
# - user: authenticated (may be newly created) user
# - **kwargs: additional data sent in the beginning of authentication
#   to scipio.forms.AuthForm.auth_redirect
# A handler may return an HttpRespose instance which will be eventually
# returned from the completion view. If omitted a standard redirect will be
# used.
authenticated = dispatch.Signal(providing_args=['user', '**kwargs'])

# Creation of a new scipio profile
# Parameters:
# - sender: created scipio.models.Profile instance
created = dispatch.Signal()

# Whitelisting a profile
# Parameters:
# - sender: whitelisted scipio.models.Profile instance
whitelist = dispatch.Signal()

