print "importing packages..."
import time
start = time.time()
import folium
from folium import plugins
from functions import *
import pandas as pd
import numpy as np
from numpy import genfromtxt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import scipy
from scipy import interpolate
from scipy.interpolate import RectSphereBivariateSpline
from pprint import pprint
from scipy.interpolate import griddata
from scipy.interpolate import interp1d
from scipy.interpolate import Rbf
import random
from scipy import sparse
from sklearn.neighbors import NearestNeighbors
from math import cos, asin, sqrt
import pprint
from geopy.distance import vincenty

def intermediates(lat_1, lon_1, lat_2, lon_2, nb_points):
    """Return a list of nb_points equally spaced points
    between p1 and p2"""
    # If we have 8 intermediate points, we have 8+1=9 spaces
    # between p1 and p2
    x_spacing = (lat_2 - lat_1) / (nb_points + 1)
    y_spacing = (lon_2 - lon_1) / (nb_points + 1)

    return [[lat_1 + i * x_spacing, lon_1 +  i * y_spacing]
            for i in range(1, nb_points+1)]

def getPoints(dataset, lat_x, lon_y, a_z, smooth, nb_points):
    if nb_points > 0:
        start = 0
        end=len(real)
        while (start < end):
            lat_1=(real[start][0])
            lon_1=(real[start][1])
            start2 = 0
            while (start2 < end):
                lat_2=(real[start2][0])
                lon_2=(real[start2][1])
                start2=start2+1
                start3 = 0
                new_cords = np.array([])
                while (start3 < end):
                    
                    interm = intermediates(lat_1,lon_1,lat_2,lon_2,nb_points)
                    interm = np.array(interm)
                    new_lat = [float(item[0]) for item in interm]
                    new_lon = [float(item[1]) for item in interm]
                    f = interpolate.Rbf(lat_x, lon_y, a_z, smooth=smooth)

                    new_a =  f(new_lat, new_lon)
                    new_set = (zip(new_lat,new_lon,new_a))
                    new_set_1 = np.array(new_set)
                    new_cords =  np.append(new_cords,new_set_1)
                    start3=start3+1
            start=start+1

        return new_cords
    else:
        print "Error in arg nb_points: Need to enter value greater than 0"


print "finished importing packages"
print "logging into google drive..."

scope = ['https://spreadsheets.google.com/feeds']

#retrieves credentials from Google Service Account to log in
credentials = ServiceAccountCredentials.from_json_keyfile_name('data.json', scope)
gc = gspread.authorize(credentials)

#import population codes spreadsheet to pandas
pops = gc.open_by_key('1nP3mdssbSH9fftb8FHq9J8tFXHI0dqcARhRJ3mMpgGY')
p_sheet = pops.sheet1
pop = pd.DataFrame(p_sheet.get_all_records())

#import cordinate spreadsheet to pandas
cords = gc.open_by_key('1c5ZbJPPIoIOdYjGtkXLjfFyUlZcN0DSgaSnkYevEdFw')
c_sheet = cords.sheet1
cord = pd.DataFrame(c_sheet.get_all_records())

#import allele spreadsheet to pandas
alleles = gc.open_by_key('1SzXv3RQIim-eYhW4-OtVjveDd9Ph6QuXSTDTXqcN0ug')
a_sheet = alleles.sheet1
al = pd.DataFrame(a_sheet.get_all_records())

#import trait info spreadsheet to pandas
traits = gc.open_by_key('1yZCN3vkQWZLQea1xOvfAb4OzfM8zqN4tQn44obWT7m4')
t_sheet = traits.sheet1
trait = pd.DataFrame(t_sheet.get_all_records())

print "retrieved sheets from google drive"

print "creating database..."

#merging data onto one database
flt = pd.merge(cord, al, copy=False, on='CODE')

res = pd.merge(flt, trait, copy=False, on='RS')

full = pd.merge(res, pop, copy=False, on='CODE')

#converts cordinate and allele data to numpy array
array = flt.as_matrix()

print "database finished and turned into array"
print "getting cordinates..."

#takes numpy array and turns data into values to go on map
lat = [float(item[1]) for item in array]
lon = [float(item[2]) for item in array]
a = [float(item[3]) for item in array]

real_zip = (zip(lat, lon))

real = np.array(real_zip)

lat_lon = (zip(lat,lon))

#new_cord(lat,lon,a,2)

print "old data"
old_data = (zip(lat,lon,a))
dataset = np.array(old_data)
print dataset

print "new data"
new_data = getPoints(dataset,lat,lon,a,2,5)
print new_data

print "got cordinates"
print "interpolating..."

#new_cord(lat, lon, a)

print "completed interpolating"
print "creating map..."

#replace stamentoner with whatever tileset is best (custom ones can be made)
m = folium.Map([48., 5.], tiles='stamentoner',control_scale = True, zoom_start=1)

#play around with radius value to see which one is best, and gradient changes heatmap colors
m.add_child(plugins.HeatMap(zip(lat, lon, a), radius = 13, gradient={.4: 'dodgerblue', .6: 'blue', 1: 'blue'}))

print "created map"

print "saving map..."
#saves heatmap as an html file
m.save('map.html')

print "map saved"

print "kind of created by Connor Caldwell"

endTime = time.time()-start

if endTime < 2:
    print '-----This program ran in', endTime, 'seconds! That was super fast!-----'
else:
    print '-----This program ran in', endTime, 'seconds. That was really slow.-----'

"""
_________
\_   ___ \  ____   ____   ____   ___________
/    \  \/ /  _ \ /    \ /    \ /  _ \_  __ \
\     \___(  <_> )   |  \   |  (  <_> )  | \/
 \______  /\____/|___|  /___|  /\____/|__|
        \/            \/     \/
"""
