import django.contrib.gis.geos
import symmetricjsonrpc
import types

class GEOSFeature(object):
    def __init__(self, *arg, **kw):
        """GEOSFeature(json_data)
           GEOSFeature(geometry, property_name1=value, property_name2=value, ...)
           GEOSFeature(geometry, id, property_name1=value, property_name2=value, ...)
           GEOSFeature(geometry, id, propertiesdict)
        """
        assert len(arg) > 0 and len(arg) <= 3

        self.geometry = None
        self.properties = {}
        self.id = None

        if isinstance(arg[0], django.contrib.gis.geos.GEOSGeometry):
            self.geometry = arg[0]
        else:
            obj = symmetricjsonrpc.from_json(arg[0])
            if obj['type'].lower() == 'feature':
                self.geometry = django.contrib.gis.geos.GEOSGeometry(symmetricjsonrpc.to_json(obj['geometry']))
                if 'properties' in obj:
                    self.properties.update(obj['properties'])
                if 'id' in obj:
                    self.id = obj['id']
            else:
                self.geometry = django.contrib.gis.geos.GEOSGeometry(arg[0])

        if len(arg) > 1:
            self.id = arg[1]

        if len(arg) > 2:
            self.properties.update(arg[2])
        self.properties.update(kw)

    @property
    def json(self):
        res = {"type": "Feature",
               "geometry": symmetricjsonrpc.from_json(self.geometry.json),
               "properties": self.properties}
        if self.id is not None:
            res['id'] = self.id
        return symmetricjsonrpc.to_json(res)
        
class GEOSFeatureCollection(object):
    def __init__(self, arg):
        """GEOSFeatureCollection(json_data)
           GEOSFeatureCollection([json_data1, json_data2, ...])
           GEOSFeatureCollection([feature1, feature2, ...])
        """
        self.features = []
        if isinstance(arg, (types.ListType, types.TupleType)):
            for feature in arg:
                if not isinstance(feature, GEOSFeature):
                    feature = GEOSFeature(feature)
                self.features.append(feature)
        else:
            obj = symmetricjsonrpc.from_json(arg)
            assert obj['type'].lower() == "featurecollection"
            for feature in obj['features']:
                self.features.append(GEOSFeature(symmetricjsonrpc.to_json(feature)))

    @property
    def json(self):
        res = {"type": "FeatureCollection",
               "features": [symmetricjsonrpc.from_json(feature.json) for feature in self.features]}
        return symmetricjsonrpc.to_json(res)
    
    def __iadd__(self, other):
        self.features += other.features
        return self

    #def __add__(self, other):
    #    return type(self)(self.features + other.features)
