# -*- coding: utf-8 -*-
import django.contrib.auth.models
from django.utils.translation import ugettext_lazy as _
import django.contrib.gis.db.models
import django.contrib.gis.geos


class Vehicle(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    name = django.contrib.gis.db.models.CharField(_('name'), max_length=256)
    description = django.contrib.gis.db.models.TextField(_('description'))
    owner = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="owned_vehicles")

    def __unicode__(self):
        return self.name



class TimePoint(django.contrib.gis.db.models.Model):
    timestamp = django.contrib.gis.db.models.DateTimeField()
    point = django.contrib.gis.db.models.PointField(geography=True)
    objects = django.contrib.gis.db.models.GeoManager()

    def __unicode__(self):
        return "%s @ %s" % (self.point, self.timestamp)


class Path(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    timestamp = django.contrib.gis.db.models.DateTimeField()
    name = django.contrib.gis.db.models.CharField(_('name'), max_length=256)
    description = django.contrib.gis.db.models.TextField(_('description'))

    @property
    def as_line_string(self):
        return django.contrib.gis.geos.LineString([point.point for point in self.points.order_by('timestamp')])

    def __unicode__(self):
        return self.name

class PathPoint(TimePoint):
    path = django.contrib.gis.db.models.ForeignKey(Path, related_name='points')



class Journey(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    vehicle = django.db.models.ForeignKey(Vehicle, related_name="journeys")
    owner = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="organized_journeys")
    name = django.contrib.gis.db.models.CharField(_('name'), max_length=256)
    description = django.contrib.gis.db.models.TextField(_('description'))

    @property
    def as_multi_line_string(self):
        return django.contrib.gis.geos.MultiLineString([path.as_line_string for path in self.paths.order_by('timestamp')])

    def __unicode__(self):
        return self.name

class JourneyPath(Path):
    journey = django.contrib.gis.db.models.ForeignKey(Journey, related_name='paths')


    
