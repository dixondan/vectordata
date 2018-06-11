
import os
from zipfile import ZipFile
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point

three_dirs = [r'path1',
             r'path2',
             r'path3']

gdf_list = []
for directory in three_dirs:
    #look trough three dirs
    files_kmz = []
    
    files = os.listdir(directory)
    for f in files:
        if f.endswith(".kmz"):
            files_kmz.append(os.path.join(directory,f))
    name = directory.split('\\')[-1]
    #get list of all kmz files
    for kmz in files_kmz:
        #print kmz
        kmz1 = ZipFile(kmz, 'r')
        kml = kmz1.open('doc.kml', 'r').read()
        #open it and get the kml string
        kml_strings = kml.split("\t\t\t")
        coords1 = []
        for s in kml_strings:
            if "coordinates" not in s:
                #sys.exit()
                pass
            if "coordinates" in s:
                coords1.append(s)
        if len(coords1) > 0:
        #get only coords fromt he string
            df = pd.DataFrame(coords1,columns = ['string'])
            df = df['string'].str.split(",", expand=True)
            df.columns = ['c1','c2','c3']
            df['lat'] = df['c1'].str.split('>').str[1]
            df['long'] = df['c2']
            df = df[['lat','long']]
            df = df.astype("float")
            geometry = [Point(xy) for xy in zip( df.lat,df.long)]
            df = df.drop(['long', 'lat'], axis=1)
            crs = {'init': 'epsg:4326'}
            gdf = GeoDataFrame(df, crs=crs, geometry=geometry)
            gdf['grid'] = kmz.split('.')[0].split('\\')[-1]
            gdf['name'] = name
            gdf_list.append(gdf)
            print directory
        else:
            print len(coords1)
       
final_df = pd.concat(gdf_list)
#final_df.plot() plot it


final_df.to_file(r"out.shp")








