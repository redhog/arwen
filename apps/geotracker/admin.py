# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
import django.contrib.gis.admin
import geotracker.models
import django.forms
import django.contrib.gis.geos

class OpenLayersInput(django.forms.CharField):
    def __init__(self, geom_type, name):
        self.geom_type = geom_type
        self.name = name
        django.forms.CharField.__init__(self)


class GeoModelAdmin(django.contrib.gis.admin.GeoModelAdmin):
    def __init__(self, *arg, **kw):
        fields = {}
        for name, value in self.form.declared_fields.iteritems():
            print name, type(value)
            if isinstance(value, OpenLayersInput):
                map_widget = self.get_map_widget(value)
                class MapInput(django.forms.CharField):
                    widget = map_widget
                fields[name] = MapInput()
        Form = type(self).form
        self.form = type(Form)("Form", (Form,), fields)

        django.contrib.gis.admin.GeoModelAdmin.__init__(self, *arg, **kw)


django.contrib.gis.admin.site.register(geotracker.models.Vehicle, django.contrib.gis.admin.GeoModelAdmin)
django.contrib.gis.admin.site.register(geotracker.models.TimePoint, django.contrib.gis.admin.GeoModelAdmin)

class PathAdminForm(django.forms.ModelForm):
    path = OpenLayersInput(geom_type = "LINESTRING", name = "path")

    class Meta:
        model = geotracker.models.Path

    def save(self, commit=True):
        instance = super(PathAdminForm, self).save(commit)
        
        instance.as_geosgeometry = django.contrib.gis.geos.fromstr(self.cleaned_data['path'])
        instance.save(commit)

        return instance

class PathAdmin(GeoModelAdmin):
    form = PathAdminForm
    fields = ['timestamp', 'name', 'description', 'path']
        
django.contrib.gis.admin.site.register(geotracker.models.Path, PathAdmin)
django.contrib.gis.admin.site.register(geotracker.models.PathPoint, django.contrib.gis.admin.GeoModelAdmin)
django.contrib.gis.admin.site.register(geotracker.models.Journey, django.contrib.gis.admin.GeoModelAdmin)

class JourneyPathAdminForm(PathAdminForm):
    class Meta:
        model = geotracker.models.JourneyPath

class JourneyPathAdmin(PathAdmin):
    form = JourneyPathAdminForm

django.contrib.gis.admin.site.register(geotracker.models.JourneyPath, JourneyPathAdmin)
