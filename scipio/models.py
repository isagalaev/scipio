from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from openid.message import OPENID_NS

from scipio import utils, signals

class ProfileManager(models.Manager):
    def from_openid(self, openid_info):
        '''
        Creates a Profile instance and a corresponding auth.User instance from
        openid info obtained from openid.consumer.complete
        '''
        try:
            profile = self.get(openid=openid_info.claimed_id)
        except self.model.DoesNotExist:
            username, nickname, autoupdate = utils.get_names(openid_info)
            user = User.objects.create_user(username, 'user@scipio', User.objects.make_random_password())
            profile = self.create(
                user = user,
                openid = openid_info.claimed_id,
                openid_server = openid_info.getSigned(OPENID_NS, 'op_endpoint'),
                nickname = nickname,
                autoupdate = autoupdate,
            )
            profile.save()
            signals.created.send(sender=profile)
        return profile

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='scipio_profile', primary_key=True)
    openid = models.CharField(_('OpenID'), max_length=200, unique=True)
    openid_server = models.CharField(_('OpenID Server'), max_length=200, blank=True)
    nickname = models.CharField(_('Nickname'), max_length=200, blank=True)
    autoupdate = models.BooleanField(_('Update automatically'), default=True, db_index=True)
    spamer = models.NullBooleanField(_('Spammer'))

    objects = ProfileManager()

    def __str__(self):

        def _pretty_url(url):
            url = url[url.index('://') + 3:]
            if url.endswith('/'):
                url = url[:-1]
            return url

        return self.nickname or _pretty_url(self.openid)

    def update_profile(self):
        '''
        Reads profile info from HTTP page and updates profile.
        Currently just reads hCard.
        '''
        data = utils.read_hcard(self.openid)
        changes = {}
        if data:
            for key, value in data.items():
                old_value = getattr(self, key)
                if old_value != value:
                    setattr(self, key, value)
                    changes[key] = (old_value, value)
        return changes

class WhitelistSource(models.Model):
    url = models.URLField(_('URL'))

    def __str__(self):
        return self.url

class CleanOpenID(models.Model):
    openid = models.CharField(_('OpenID'), max_length=200, db_index=True)
    source = models.ForeignKey(WhitelistSource, verbose_name=_('Source'))

    class Meta:
        unique_together = [('openid', 'source')]
        ordering = ['openid']
        verbose_name = 'Clean OpenID'
        verbose_name_plural = 'Clean OpenIDs'

    def __str__(self):
        return self.openid
