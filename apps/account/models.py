import django.db.models

import django.contrib.auth.models
from django.utils.translation import ugettext_lazy as _

class UserInfo(django.contrib.auth.models.User):
    user = django.db.models.OneToOneField(django.contrib.auth.models.User, related_name="info")

    phone = django.db.models.CharField(_('phone'), max_length=256)
    public_phone = django.db.models.BooleanField(_('public'), default=False)
    public_email = django.db.models.BooleanField(_('public'), default=False)

    def __unicode__(self):
        return self.user.username
