from optparse import make_option
import logging

from django.core.management.base import NoArgsCommand

log = logging.getLogger('scipio')

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--quiet', action='store_true', dest='quiet', default=False,
            help='Do not display messages other than errors'),
    )
    help = 'Updates OpenID "white lists" from external sources'

    def handle_noargs(self, quiet=False, **base_options):
        from scipio.models import CleanOpenID, WhitelistSource
        from urllib2 import urlopen, Request
        for source in WhitelistSource.objects.all():
            try:
                f = urlopen(Request(source.url, headers={'Accept': 'text/plain'}))
                source.cleanopenid_set.all().delete()
                source.cleanopenid_set = [CleanOpenID(openid=l.strip()) for l in f]
                if not quiet:
                    log.info('Updated %s OpenIDs from %s' % (source.cleanopenid_set.count(), source))
            except IOError, e:
                log.error('Reading %s: %s' % (source, e))
