# -*- coding:utf-8 -*-
from optparse import make_option
import logging

from django.core.management.base import NoArgsCommand
from django.utils.encoding import smart_str

log = logging.getLogger('scipio')

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--quiet', action='store_true', dest='quiet', default=False,
            help=u'Do not display messages other than errors'),
    )
    help = u'Updates profile data from OpenID urls'

    def handle_noargs(self, quiet=False, **base_options):
        from scipio.models import Profile
        for profile in Profile.objects.filter(autoupdate=True):
            try:
                changes = profile.update_profile()
                if not changes:
                    continue
                profile.save()
                if not quiet:
                    changes_str = '; '.join('%s: %s -> %s' % (
                        k,
                        smart_str(ov),
                        smart_str(nv),
                    ) for k, (ov, nv) in changes.items())
                    log.info('Updated profile ID=%s: %s' % (profile.pk, changes_str))
            except Exception, e:
                log.error('Profile ID=%s: %s' % (profile.pk, e))
