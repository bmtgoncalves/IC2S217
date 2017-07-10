# Adapted from code & formulas by David Z. Creemer and others
# http://www.zachary.com/blog/2005/01/12/python_zipcode_geo-programming
# http://williams.best.vwh.net/avform.htm
#

from math import sin,cos,atan,acos,asin,atan2,sqrt,pi, modf

# At the equator / on another great circle???
nauticalMilePerLat = 60.00721
nauticalMilePerLongitude = 60.10793

rad = pi / 180.0

milesPerNauticalMile = 1.15078
kmsPerNauticalMile = 1.85200

degreeInMiles = milesPerNauticalMile * 60
degreeInKms = kmsPerNauticalMile * 60

# earth's mean radius = 6,371km
earthradius = 6371.0

def getDistance(loc1, loc2):
    "aliased default algorithm; args are (lat_decimal,lon_decimal) tuples"
    
    return getDistanceByHaversine(loc1, loc2)

def getDistanceByHaversine(loc1, loc2):
    "Haversine formula - give coordinates as (lat_decimal,lon_decimal) tuples"

    lat1, lon1 = loc1
    lat2, lon2 = loc2
    # convert to radians
    lon1 = lon1 * pi / 180.0
    lon2 = lon2 * pi / 180.0
    lat1 = lat1 * pi / 180.0
    lat2 = lat2 * pi / 180.0

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2.0))**2
    c = 2.0 * atan2(sqrt(a), sqrt(1.0-a))
    km = earthradius * c
    return km

