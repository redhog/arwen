# -*- coding: utf-8 -*-
import django.contrib.auth.models
from django.utils.translation import ugettext_lazy as _
import django.contrib.gis.db.models
import geotracker.geos

class Vehicle(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    name = django.contrib.gis.db.models.CharField(_('name'), max_length=256)
    description = django.contrib.gis.db.models.TextField(_('description'))
    owner = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="owned_vehicles")

    def __unicode__(self):
        return self.name



class TimePoint(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    timestamp = django.contrib.gis.db.models.DateTimeField()
    point = django.contrib.gis.db.models.PointField(geography=True)

    @property
    def as_geosgeometry(self):
        return geotracker.geos.GEOSFeature(self.point, self.id, timestamp = self.timestamp)

    @property
    def as_geoscollection(self):
        return geotracker.geos.GEOSFeatureCollection([self.as_geosgeometry])

    def __unicode__(self):
        return "%s @ %s" % (self.point, self.timestamp)


class Path(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()

    timestamp = django.contrib.gis.db.models.DateTimeField()
    name = django.contrib.gis.db.models.CharField(_('name'), max_length=256)
    description = django.contrib.gis.db.models.TextField(_('description'))

    @property
    def as_geosgeometry(self):
        return geotracker.geos.GEOSFeature(django.contrib.gis.geos.LineString([point.point for point in self.points.order_by('timestamp')]),
                                           self.id,
                                           name = self.name,
                                           description = self.description)
    @property
    def as_geoscollection(self):
        res = geotracker.geos.GEOSFeatureCollection([self.as_geosgeometry])
        for point in self.points.order_by('timestamp'):
            res += point.as_geoscollection
        return res

    def __unicode__(self):
        return self.name

class PathPoint(TimePoint):
    path = django.contrib.gis.db.models.ForeignKey(Path, related_name='points')

    @property
    def as_geosgeometry(self):
        return geotracker.geos.GEOSFeature(self.point, self.id, timestamp = self.timestamp, path = self.path.id)


class Journey(django.contrib.gis.db.models.Model):
    objects = django.contrib.gis.db.models.GeoManager()
    vehicle = django.db.models.ForeignKey(Vehicle, related_name="journeys")
    owner = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="organized_journeys")
    name = django.contrib.gis.db.models.CharField(_('name'), max_length=256)
    description = django.contrib.gis.db.models.TextField(_('description'))

    @property
    def as_geosgeometry(self):
        return geotracker.geos.GEOSFeature(django.contrib.gis.geos.MultiLineString([path.as_geosgeometry for path in self.paths.order_by('timestamp')]),
                                           self.id,
                                           vehicle = self.vehicle.id,
                                           owner = self.owner.id,
                                           name = self.name,
                                           description = self.description)
    @property
    def as_geoscollection(self):
        res = geotracker.geos.GEOSFeatureCollection([self.as_geosgeometry])
        for path in self.paths.order_by('timestamp'):
            res += path.as_geoscollection
        return res

    def __unicode__(self):
        return self.name

class JourneyPath(Path):
    journey = django.contrib.gis.db.models.ForeignKey(Journey, related_name='paths')


    
