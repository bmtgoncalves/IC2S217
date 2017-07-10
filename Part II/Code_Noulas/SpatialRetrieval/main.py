##########################################
# Reading CSV file with Airbnb Listings  #
# Data from insideairbnb.com/			 # 
##########################################

#read a csv file with location information
#let's start with Airbnb listings 
import csv
import random  

input_file = csv.DictReader(open('london_listings.csv'))

#CSV headers: id,name,host_id,host_name,neighbourhood_group,neighbourhood,latitude,longitude,room_type,price,minimum_nights,number_of_reviews,last_review,reviews_per_month,calculated_host_listings_count,availability_365

airbnb_listings = {}  # dictionary key is listing id, values are listing info in a python <list>
for row in input_file:

	if random.random() > 1.0: #control sample size: 100% here 
		continue


	listing_id = row['id']
	latitude = row['latitude']
	longitude = row['longitude']
	num_reviews = row['number_of_reviews']
	price = row['price']

	airbnb_listings[listing_id] = [float(latitude), float(longitude), num_reviews, float(price)]


num_listings = len(airbnb_listings)
print 'Number of Airbnb listings in London: ' + str(num_listings)


##################################################
# Reading Arbitrary Data File: London locations  #
##################################################

#open file with 'read' permissions
#file format : venue_id*;*(latitude, longitude, categry, #users, #check-ins, place title)
#example: 4b8e5ed2f964a520621f33e3*;*(51.514180000000003, -0.090876125000000002, 'Other - Food', '218', '288', 'Browns Bar and Brasserie')

f_in = open('London_locationData_foursquare.txt', 'r')
foursquare_venues = {}
for line in f_in:
	splits = line.split('*;*')
	venueid = splits[0]
	info = eval(splits[1])
	foursquare_venues[venueid] = info


##################################################
# Geographic Analysis: Measure Distances		 #
##################################################

import sys
import pylab
sys.path.append('./location_central/') #adding directory to python path
import geolocator

num_samples = 1000
airbnb_distances = []
foursquare_distances = []
for i in xrange(0, num_samples):

	#sample two airbnb venues
	listing1 = random.choice(airbnb_listings.keys())
	listing2 = random.choice(airbnb_listings.keys())

	#sample two foursquare venues
	venue1 = random.choice(foursquare_venues.keys())
	venue2 = random.choice(foursquare_venues.keys())

	air_distance = geolocator.getDistance(airbnb_listings[listing1][0:2], airbnb_listings[listing2][0:2])
	venue_distance= geolocator.getDistance(foursquare_venues[venue1][0:2], foursquare_venues[venue2][0:2])

	airbnb_distances.append(air_distance)
	foursquare_distances.append(venue_distance)

#filtering out extreme values
airbnb_distances = [d for d in airbnb_distances if d < 50]
foursquare_distances = [d for d in foursquare_distances if d < 50]

pylab.title('Distances between two randomly picked places')
pylab.ylabel('Frequency')
pylab.xlabel('Distance [km]')
pylab.hist(airbnb_distances, alpha=0.5, label='Airbnb')
pylab.hist(foursquare_distances, alpha=0.5, label='Foursquare')
pylab.legend()
pylab.savefig('./graphs/distances.pdf')


##################################################
# Geographic Analysis: Get City Center   		 #
##################################################
import numpy 

lats = []
longits = []
for venueid, info in foursquare_venues.items():
	lats.append(info[0])
	longits.append(info[1])

mean_lat = numpy.median(lats)
mean_long = numpy.median(longits)
city_center = (mean_lat, mean_long)

print 'The center of London is at Latitude: %f and Longitude: %f' %(mean_lat, mean_long)
print 'Copy paste the pair of numbers representing the center on google maps search and check sanity: %f, %f ' %(mean_lat, mean_long)

#### Exercise: Let's do the same with Airbnb ####


lats = []
longits = [] 
for listing_id, listing_info in airbnb_listings.items():
	lats.append(listing_info[0])
	longits.append(listing_info[1])

mean_lat = numpy.median(lats)
mean_long = numpy.median(longits)
city_center = (mean_lat, mean_long)
print 'The "airbnb" center of London is at Latitude: %f and Longitude: %f' %(mean_lat, mean_long)
print 'Copy paste the pair of numbers representing the center on google maps search and check sanity: %f, %f ' %(mean_lat, mean_long)


#####################################################
# Object Oriented Programming: Saves time and money!#
#####################################################
import SpatialRetriever as SR

srAirbnb = SR.SpatialRetriever(airbnb_listings)
srFoursquare = SR.SpatialRetriever(foursquare_venues)

print srAirbnb.get_city_center()
print srFoursquare.get_city_center()

#Get the locations within 200 meters radius from the Foursquare city center
fourquare_center = srFoursquare.get_city_center()
nearby_locations_4sq = srFoursquare.get_nearby_locations(fourquare_center[0], 
	fourquare_center[1], 0.2, area_shape='circle')

airbnb_center = srAirbnb.get_city_center()
nearby_locations_airbnb = srAirbnb.get_nearby_locations(airbnb_center[0], 
	airbnb_center[1], 0.2, area_shape='circle')



##################################################
# Visualise results using folium  				 #
##################################################
import folium 

mymap = folium.Map(location=[city_center[0], city_center[1]], zoom_start=14)

#plot city center as a coloured circle
folium.CircleMarker(location=fourquare_center, radius=100,
                    popup='Foursquare Centre', color='#3186cc',
                    fill_color='#3186cc').add_to(mymap)

#plot city center as a coloured circle
folium.CircleMarker(location=airbnb_center, radius=100,
                    popup='Airbnb Centre', color='#cc3131',
                    fill_color='#cc3131').add_to(mymap)


for loc_id in nearby_locations_4sq:
	folium.CircleMarker(srFoursquare.locationData[loc_id][0:2], radius = 5, color='#3186cc',
                    fill_color='#2186ac').add_to(mymap)

for loc_id in nearby_locations_airbnb:
	folium.CircleMarker(srAirbnb.locationData[loc_id][0:2], radius = 5, color='#cc3131',
                    fill_color='#cc3131').add_to(mymap)

mymap.save('./graphs/MappingCityCenters.html')

