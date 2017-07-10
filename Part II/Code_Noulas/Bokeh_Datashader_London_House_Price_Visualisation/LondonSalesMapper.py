from bokeh.io import show
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper
)
from bokeh.palettes import Viridis6 as palette
from bokeh.plotting import figure
import numpy as np
import pylab as plt 
import pygeoj
import csv

import datashader as ds
from functools import partial
from datashader.utils import export_image
from datashader.colors import colormap_select, Greys9, Hot, viridis, inferno
from IPython.core.display import HTML, display
from bokeh.plotting import figure 
import pandas as pd
from datashader import transfer_functions as tf



class LondonSalesMapper:

    def __init__(self):
        pass


    def load_lsoa_polygons(self):
        polygon_data = pygeoj.load(filepath="LondonLSOA.geojson")
        spatial_entity_to_coordinates = {}

        for feature in polygon_data:
            coords = feature.geometry.coordinates
            coords = coords[0][0]
            lsoa_id = feature.properties['LSOA11CD']

            xs = [i for i,j in coords]
            ys = [j for i,j in coords]
            spatial_entity_to_coordinates[lsoa_id] = [xs,ys]
        
        return spatial_entity_to_coordinates



    def load_lsoa_price_values(self):
        entity_to_prices = {}

        with open('london_sales_2013_2014.csv', 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    lsoa_id = row['lsoa11']
                    price = float(row['price'])
                    date = row['year_month']
                    entity_to_prices.setdefault(lsoa_id, [])
                    entity_to_prices[lsoa_id].append(price)
                except: 
                    continue

        #average 
        for entity, all_prices in entity_to_prices.items():
            entity_to_prices[entity] = np.median(all_prices)

        return entity_to_prices




    def plot_sales_mapstogram(self, year=None):

        #define a bounding box around London
        london = [-0.535583, 51.73, 0.334, 51.23 , 'london']

        #read postcode frequency data: y_col,x_col,year: 51.464568,0.161226,1995
        df = pd.read_csv('postcode_freq_data.csv')

        city = london 
        maxLong = city[2]
        minLong = city[0]
        maxLat = city[1]
        minLat = city[3]

        #filter out "noisy" data
        if year == None:
            df = df.loc[(df['x_col'] < maxLong) & (df['x_col'] > minLong) & (df['y_col'] > minLat) & (df['y_col'] < maxLat)] 
        else:
            #consider annual filtering
            df = df.loc[(df['x_col'] < maxLong) & (df['x_col'] > minLong) & (df['y_col'] > minLat) & (df['y_col'] < maxLat) & (df['year'] == year)] 

        print (df.tail())

        LDN = x_range, y_range = ((minLong,maxLong), (minLat, maxLat))

        #define resolution of image: may need to change for varying data volumes
        plot_width  = int(1500)
        plot_height = int(plot_width//1.2)
        background = "black"
        export = partial(export_image, export_path="export", background=background)

        def create_image(x_range, y_range, w=plot_width, h=plot_height):
            #set up canvas and populate with datapoints
            cvs = ds.Canvas(plot_width=w, plot_height=h, x_range=x_range, y_range=y_range)
            agg = cvs.points(df, 'x_col', 'y_col')
            img = tf.shade(agg, cmap=Hot, how='eq_hist')
            return tf.dynspread(img, threshold=0.5, max_px=4)

        export(create_image(*LDN), city[4] + '_' +  str(year) + '_hot')



    def plot_bokeh_intensity_map(self, spatial_entity_to_coordinates, spatial_entity_to_values):

        entity_xs = []
        entity_ys = []
        entity_names = []
        entity_rates = []
        for name, coords in spatial_entity_to_coordinates.items():
            xs = [i for i in coords[0]]
            ys = [i for i in coords[1]] 
            try:
                intensity_value = np.median(spatial_entity_to_values[name])
            except:
                intensity_value = 0.0

            entity_xs.append(xs)
            entity_ys.append(ys)
            entity_names.append(name)
            entity_rates.append(intensity_value)

        palette.reverse()
        color_mapper = LogColorMapper(palette=palette)


        source = ColumnDataSource(data=dict(
            x=entity_xs,
            y=entity_ys,
            name=entity_names,
            rate=entity_rates,
        ))

        TOOLS = "pan,wheel_zoom,reset,hover,save"

        p = figure(
            title="London Median House Prices, 2013-2014", tools=TOOLS,
            x_axis_location=None, y_axis_location=None
        )
        p.grid.grid_line_color = None

        p.patches('x', 'y', source=source,
                  fill_color={'field': 'rate', 'transform': color_mapper},
                  fill_alpha=0.7, line_color="white", line_width=0.5)

        hover = p.select_one(HoverTool)
        hover.point_policy = "follow_mouse"
        hover.tooltips = [
            ("Name", "@name"),
            ("Price change rate)", "@rate%"),
            ("(Long, Lat)", "($x, $y)"),
        ]

        show(p)


if __name__ == '__main__':
    ls  = LondonSalesMapper()
    ls.plot_sales_mapstogram()

    spatial_entity_to_coordinates = ls.load_lsoa_polygons() #load London's LSOA areas as polygons (set of coordinate points)
    spatial_entities_to_values = ls.load_lsoa_price_values() #load a value for each LSOA polygon in London

    ls.plot_bokeh_intensity_map(spatial_entity_to_coordinates, spatial_entities_to_values) #create an interactive map using Bokeh
