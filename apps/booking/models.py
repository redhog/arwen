# -*- coding: utf-8 -*-
import django.db.models
import django.contrib.auth.models
from django.utils.translation import ugettext_lazy as _

class Event(django.db.models.Model):
    name = django.db.models.CharField(_('name'), max_length=256)
    description = django.db.models.TextField(_('description'))
    owner = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="events")

    @property
    def sorted_dates(self):
        return self.dates.order_by("date")

    def __unicode__(self):
        return self.name

class EventDate(django.db.models.Model):
    date = django.db.models.DateField(_('date'))
    event = django.db.models.ForeignKey(Event, related_name="dates")

    def __unicode__(self):
        return "%s @ %s" % (self.event, self.date)

class EventBooking(django.db.models.Model):
    booker = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="event_bookings")
    event = django.db.models.ForeignKey(Event, related_name="bookings")
    comment = django.db.models.TextField(_('comment'))

    @property
    def sorted_dates(self):
        return self.dates.order_by("date__date")

    def __unicode__(self):
        return "%s @ %s" % (self.booker, self.event)


class EventDateBooking(django.db.models.Model):
    event_booking = django.db.models.ForeignKey(EventBooking, related_name="dates")
    date = django.db.models.ForeignKey(EventDate, related_name="bookings")

    def __unicode__(self):
        return "%s @ %s" % (self.event_booking, self.date.date)

