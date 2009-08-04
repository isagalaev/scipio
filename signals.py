# -*- coding:utf-8 -*-
from django import dispatch

# Sent upon a successfull completion of OpenID authentication
# Parameters:
# - sender: HttpRequest instance
# - user: authenticated (may be newly created) user
# - **kwargs: additional data sent in the beginning of authentication
#   to scipio.forms.AuthForm.auth_redirect
authenticated = dispatch.Signal(providing_args=['user', '**kwargs'])

# Sent upon creation of a new scipio profile
# Parameters:
# - sender: created scipio.models.Profile instance
created = dispatch.Signal()
