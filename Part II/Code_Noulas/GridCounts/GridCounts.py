#################################################################
# Uber Surge Prediction Using: Foursquare, Airbnb and Taxi Data #
#################################################################

import csv
import numpy as np

lonMin = -74.1  # minimum longitude
lonMax = -73.7
lonStep = 0.0025  # defines cell size

latMin = 40.6  # minimum latitude
latMax = 41.0
latStep = 0.0025  # defines cell size

latLen = int((latMax - latMin) / latStep) + 1  # number of cells on the y-axis
lonLen = int((lonMax - lonMin) / lonStep) + 1  # number of cells on the x-axis

# Cell counts for each source of geo-data
FSQcellCount = np.zeros((latLen, lonLen))
AIRcellCount = np.zeros((latLen, lonLen))
TAXIcellCount = np.zeros((latLen, lonLen))


####### LOADING COORDS FROM 3 GEO LAYERS #########
airbnb_coords = []

with open('listings_sample.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        airbnb_coords.append([float(row['latitude']), float(row['longitude'])])

print('Number of Airbnb listings: ' + str(len(airbnb_coords)))


#reading Foursquare venue data #
foursquare_coords = []
with open('venue_data_4sq_newyork_anon.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        foursquare_coords.append(
            [float(row['latitude']), float(row['longitude'])])

print('Number of Foursquare listings: ' + str(len(foursquare_coords)))

#reading Taxi journey coords #
taxi_coords = []
with open('taxi_trips.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        taxi_coords.append([float(row['latitude']), float(row['longitude'])])

print('Number of Yellow Taxi journeys: ' + str(len(taxi_coords)))

############ ############ ############ ############ ############
# Counting occurrences per data layer and storing to matrix ###
############ ############ ############ ############ ############

all_coords = [foursquare_coords, airbnb_coords, taxi_coords]
for i in xrange(0, 3):
    current_coords = all_coords[i]

    for coords in current_coords:
        lat = coords[0]
        longit = coords[1]

        # if outside the grid then ingore point
        if (lat < latMin) or (lat > latMax) or (longit < lonMin) or (longit > lonMax):
            continue

        # if outside the grid then ingore point
        cx = int((longit - lonMin) / lonStep)
        cy = int((lat - latMin) / latStep)

        if i == 0:
            FSQcellCount[cy, cx] += 1
        elif i == 1:
            AIRcellCount[cy, cx] += 1
        else:
            TAXIcellCount[cy, cx] += 1


#### PLOT BOX COUNTS #####
import pylab
cdict = {'red': ((0.0, 0.0, 0.0),
                 (0.5, 1.0, 0.7),
                 (1.0, 1.0, 1.0)),
         'green': ((0.0, 0.0, 0.0),
                   (0.5, 1.0, 0.0),
                   (1.0, 1.0, 1.0)),
         'blue': ((0.0, 0.0, 0.0),
                  (0.5, 1.0, 0.0),
                  (1.0, 0.5, 1.0))}
mapIndex=0
for cellCount in [AIRcellCount,FSQcellCount,TAXIcellCount]:
	my_cmap = pylab.matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict,256)
	mapIndex +=1
	pylab.pcolor(cellCount,cmap=my_cmap)
	pylab.colorbar()
	pylab.savefig('map' + str(mapIndex) + '.pdf')
	pylab.close()



###############################################################
## PLOT A STREET NETWORK 									#####
#http://geoffboeing.com/2016/11/osmnx-python-street-networks/###
###############################################################

import osmnx as ox
G = ox.graph_from_place('Los Angeles, California', network_type='drive')
ox.plot_graph(G)

#################################################################


##################### END ###############################
