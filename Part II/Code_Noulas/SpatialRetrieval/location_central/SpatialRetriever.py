import sys
import numpy as np
import math
from math import *
from sets import Set
import geolocator
import random


class SpatialRetriever:
    '''The Spatial Retriever is a module optimized for spatial queries.'''
    def __init__(self, spatialElements):
        self.spatialElements = spatialElements
        self.load_location_data()


    def load_location_data(self):
        self.allLatLongs = []
        self.allLatsDict = {}
        self.allLongsDict = {}
        self.allLats = []
        self.allLongs = []
        self.locationData = {}

        for spatialElementId in self.spatialElements:
            [latFloat, longFloat] = self.spatialElements[spatialElementId][0:2]
            try:
                self.locationData[spatialElementId] = [latFloat,longFloat]
            except:
                print sys.exc_info()
                continue

            if self.allLatsDict.has_key(latFloat):
                self.allLatsDict[latFloat].append(spatialElementId)
            else:
                self.allLatsDict[latFloat] = [spatialElementId]

            if self.allLongsDict.has_key(longFloat):
                self.allLongsDict[longFloat].append(spatialElementId)
            else:
                self.allLongsDict[longFloat] = [spatialElementId]

            self.allLats.append(latFloat)
            self.allLongs.append(longFloat)

            self.allLatLongs.append((latFloat, longFloat))

        self.allLats.sort()
        self.allLongs.sort()


        ### append values to global location variables
        print 'Appending Values to Global Variables in Spatial Retriever Object'
        print 'Number of venues loaded:!: %d' %(len(self.allLats))
 



    def binary_search_optimized(self,sec,item):
        left = 0
        right = len(sec) - 1
        while True:
            mid = (left+right)/2
            if item < sec[mid]:
                right = mid
            else:
                left = mid

            if right ==  left+1:
                return sec[left:left+2]



    def get_nearby_locations(self,latitude,longitude,distance,area_shape='square'):
         #returns nearby locations given a point
        ([lat_up,lat_down],[long_left,long_right]) = self.get_rectangle_coordinates(latitude,longitude,distance)
        #get lat list values
        lat_left_limit_value = self.binary_search_optimized(self.allLats,lat_down)[1]
        lat_right_limit_value = self.binary_search_optimized(self.allLats,lat_up)[0]

        #...and indices
        lat_left_limit_index = self.allLats.index(lat_left_limit_value)
        lat_right_limit_index = self.allLats.index(lat_right_limit_value)

        #get long list values
        long_left_limit_value = self.binary_search_optimized(self.allLongs,long_left)[1]
        long_right_limit_value = self.binary_search_optimized(self.allLongs,long_right)[0]

        #...and indices
        long_left_limit_index = self.allLongs.index(long_left_limit_value)
        long_right_limit_index = self.allLongs.index(long_right_limit_value)

        #now get all locations from latitutde and longitude lists that satisfy those constraints
        all_valid_lats = self.allLats[lat_left_limit_index:lat_right_limit_index+1]
        all_valid_longs = self.allLongs[long_left_limit_index:long_right_limit_index+1]

        all_locs_from_lat_list  = [self.allLatsDict[lat] for lat in all_valid_lats]
        all_locs_from_long_list = [self.allLongsDict[longit] for longit in all_valid_longs]

        all_lat_locs_cleared = []
        for locs in all_locs_from_lat_list:
            for loc in locs:
                all_lat_locs_cleared.append(loc)

        all_long_locs_cleared = []
        for locs in all_locs_from_long_list:
            for loc in locs:
                all_long_locs_cleared.append(loc)

        latSet = Set(all_lat_locs_cleared)
        longSet = Set(all_long_locs_cleared)

        all_locs_in_square_set = latSet.intersection(longSet)

        location_list_insquare = list(all_locs_in_square_set)

        if area_shape == 'square':
            return location_list_insquare

        elif area_shape == 'circle':
            location_list_incircle = []
            for location in location_list_insquare:
                if geolocator.getDistance([latitude,longitude],self.locationData[location][0:2]) <= distance:
                    location_list_incircle.append(location)
            return location_list_incircle




    def get_rectangle_coordinates(self,latitude,longitude,distance):
        d = distance    #distance in km
        R = 6371.0            #earth radius in km

        lat1 = latitude
        long1 = longitude

        #convert to radians
        long1 = long1 * pi / 180.0
        lat1 = lat1 * pi / 180.0

        #case 1: lat1 == lat2
        lat_up = lat1 + 2.0*asin(1.0/2.0 * sqrt(-sqrt(-4*pow(tan(d/(2.0*R)), 2) +1) +1)*sqrt(2))             #up
        lat_down = lat1 - 2.0*asin(1.0/2.0 * sqrt(-sqrt(-4*pow(tan(d/(2.0*R)), 2) +1) +1)*sqrt(2))         #down
        #case 2: long1 == long2
        long_right = long1 + 2.0*asin(1.0/2.0 * sqrt(-sqrt(-4*pow(tan(d/(2.0*R)), 2) +1) +1)*sqrt(2)/pow(cos(lat1),1))                #right
        long_left = long1 - 2.0*asin(1.0/2.0 * sqrt(-sqrt(-4*pow(tan(d/(2.0*R)), 2) +1) +1)*sqrt(2)/pow(cos(lat1),1))   #left

        # convert from radians
        lat_up = lat_up / pi * 180.0
        lat_down = lat_down / pi * 180.0
        long_left = long_left / pi * 180.0
        long_right = long_right / pi * 180.0

        lat2 = [lat_up,lat_down]                  #up,down
        long2 = [long_left,long_right]         #left,right

        return (lat2,long2)


    def getTopDictionaryKeys(self,dictionary,number):
        topList = []
        a = dict(dictionary)
        for i in range(0,number):
            m = max(a, key=a.get)
            topList.append([m,a[m]])
            del a[m]

        return topList


    def get_city_center(self):
        return (np.median(self.allLats), np.median(self.allLongs))


    def area_recursive_splitter_v2(self,latitude,longitude,distance,numberOfSquares):
        #split an area in squares of certain minimum size: number of squares better be power of 4
        ([lat_up,lat_down],[long_left,long_right]) = self.get_rectangle_coordinates(latitude,longitude,distance/2.0)
        if numberOfSquares >= 4: #check
            newDist = distance/2.0
            newNumberOfSquares = numberOfSquares/4

            #0.86*
            pointsNW = self.area_recursive_splitter_v2(lat_up,long_left,newDist,newNumberOfSquares)
            pointsNE = self.area_recursive_splitter_v2(lat_up,long_right,newDist,newNumberOfSquares)
            pointsSE = self.area_recursive_splitter_v2(lat_down,long_right,newDist,newNumberOfSquares)
            pointsSW = self.area_recursive_splitter_v2(lat_down,long_left,newDist,newNumberOfSquares)

            return pointsSE + pointsSW + pointsNW + pointsNE
        else:
            return [(latitude,longitude)]


