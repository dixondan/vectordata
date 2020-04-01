# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 08:46:56 2020

@author: 22631228
"""

import geopandas as gpd
import rasterio
import pandas as pd
import fiona
from osgeo import gdal
import os
import numpy as np
from shapely.geometry import Point
from shapely.geometry import Polygon


#converting polygon centroid to square geometry for output
def centroid_2_polygon(row, x_size, y_size):
    x1 = row['x']
    y1 = row['y']
    halfx = np.abs(x_size / 2)
    halfy = np.abs(y_size / 2) 
    topleft =  (x1 - halfx, y1 + halfy)
    topright = (x1 + halfx, y1 + halfy)
    botright = (x1 + halfx, y1 - halfy)
    botleft = (x1 - halfx, y1 - halfy)    
    poly = Polygon(np.array([topleft, topright, botright, botleft, topleft]))
    return (poly)

#converting raster to polygon fishnet
def ras_2_fish(ras, outname):
    r = gdal.Open(ras)
    band = r.GetRasterBand(1) #bands start at one
    a = band.ReadAsArray().astype(np.float)
    (y_index, x_index) = np.nonzero(a > 0)
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = r.GetGeoTransform()
    x_coords = x_index * x_size + upper_left_x + (x_size / 2) #add half the cell size
    y_coords = y_index * y_size + upper_left_y + (y_size / 2)  
    df = pd.DataFrame()
    df['x'] = x_coords
    df['y'] = y_coords
    geometry = [Point(xy) for xy in zip(df.x, df.y)]
    crs = {'init': 'epsg:32750'}
    gdf = gpd.GeoDataFrame(df, geometry = geometry, crs = crs)
    gdf['geometry'] = gdf.apply(lambda row: centroid_2_polygon(row, x_size, y_size),axis=1)
    gdf['ID1'] = [str(i) + "_ID" for i in range(0, len(gdf))]
    outname = outname
    gdf = gdf.drop(['x', 'y'], axis=1)    
    #add the final intersection only include those squares that intersect  study_range_inside.shp
    #study_range_inside = gpd.read_file(r"/Users/danieldixon/Desktop/dandaragan/DRONE_IMAGE_COREGISTRATION/study_range_inside.shp")
    #gdf_subset = gpd.overlay(gdf,study_range_inside, how='intersection')
    gdf.to_file(outname)



raster = r"D:\#DATA\ee_2020\Planet\template6m2.tif"
outname = r"D:\#DATA\ee_2020\Planet\template6m_32750.shp"


ras_2_fish(raster, outname)


df = gpd.read_file(outname)

#df['centroid'] = df.centroid
df['geometry'] = df.centroid
#df = gpd.GeoDataFrame(df, geometry = df['centroid'], crs = df.crs)
df.to_file(r"D:\#DATA\ee_2020\Planet\template6m_32750_centroid.shp")










