# -*- coding: utf-8 -*-
import django.db.models
import django.contrib.auth.models
from django.utils.translation import ugettext_lazy as _

class Event(django.db.models.Model):
    name = django.db.models.CharField(_('name'), max_length=256)
    description = django.db.models.TextField(_('description'))
    owner = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="events")

    min_bookings = django.db.models.IntegerField(_('min_bookings'))
    ideal_bookings = django.db.models.IntegerField(_('ideal_bookings'))
    max_bookings = django.db.models.IntegerField(_('max_bookings'))

    @property
    def sorted_dates(self):
        return self.dates.order_by("date")

    def __unicode__(self):
        return self.name

class EventDate(django.db.models.Model):
    date = django.db.models.DateField(_('date'))
    event = django.db.models.ForeignKey(Event, related_name="dates")

    @property
    def color(self):
        count = self.bookings.count() - self.event.min_bookings
        ideal = self.event.ideal_bookings - self.event.min_bookings
        maxb = self.event.max_bookings - self.event.min_bookings

        if count < 0 or count > maxb:
            return "#ff0000"

        if count <= ideal:
            p = float(count) / ideal
        else:
            count -= ideal
            maxb -= ideal
            p = float(maxb - count) / maxb
        
        p = int(p * 4)
        return ['#eeffee',
                '#ccffcc',
                '#88ff88',
                '#44ff44',
                '#00ff00'][p]


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

