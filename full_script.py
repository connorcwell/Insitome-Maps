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

def distance(lat1,lng1,lat2,lng2):
    '''calculates the distance between two lat, long coordinate pairs'''
    R = 6371000 # radius of earth in m
    lat1rads = np.radians(lat1) #converts the points into radians
    lat2rads = np.radians(lat2)
    deltaLat = np.radians((lat2-lat1))
    deltaLng = np.radians((lng2-lng1))
    a = np.sin(deltaLat/2) * np.sin(deltaLat/2) + np.cos(lat1rads) * np.cos(lat2rads) * np.sin(deltaLng/2) * np.sin(deltaLng/2) #haversine formula (nick was right, he did intrigue me)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = R * c
    return d


def closest(data, lat_data, lon_data, lat, lon):
    """
    finds the closest point to the point specified within the dataset
    the lat_data and lon_data are numpy arrays of the lat and lon from the dataset (have to be seperate) 

    """
    return min(data, key=lambda p: distance(lat,lon,lat_data,lon_data))

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
    """
    returns an array of midpoints

    """
    if nb_points > 0:
        start = 0
        end=len(real)
        new_cords = np.array([])
        while (start < end):
            lat_1=(real[start][0])
            lon_1=(real[start][1])
            start2 = 0
            while (start2 < end):
                lat_2=(real[start2][0])
                lon_2=(real[start2][1])
                start2=start2+1
                start3 = 0

                while (start3 < end):
                    clos = closest(dataset, lat_x, lon_y, lat_1, lon_1)
                    print clos
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
            n = len(new_cords)/3
        return np.reshape(new_cords, (n,3))
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

real_zip = (zip(lat, lon)) #creates list that only has lat and lon to be used in function getPoints
real = np.array(real_zip) #converts the list to numpy array so the lat and lon can be accessed

lat_lon = (zip(lat,lon))

old_data = (zip(lat,lon,a)) 
dataset = np.array(lat_lon)

new_data = getPoints(dataset,lat,lon,a,0,1) 

data_cord = np.concatenate((old_data,new_data)) #merges the original set of cordinates and the interpolated cordinates 


print "got cordinates"

print "creating map..."

#replace stamentoner with whatever tileset is best (custom ones can be made)
m = folium.Map([48., 5.], tiles='stamentoner',control_scale = True, zoom_start=1)

#play around with radius value to see which one is best, and gradient changes heatmap colors
m.add_child(plugins.HeatMap(data_cord, radius = 10, gradient={.2: 'blue', .4: 'yellow', .6: 'orange', .8: 'red', 1: 'white'}))

print "created map"

print "saving map..."
#saves heatmap as an html file
m.save('map.html')
print "map saved"

print "kind of created by Connor Caldwell"

endTime = time.time()-start

if endTime < 2:
    print '-----This program ran in', endTime, 'seconds! That was super fast!-----' #got bored over the weekend so I made this :)
else:
    print '-----This program ran in', endTime, 'seconds. That was really slow.-----'

"""
_________
\_   ___ \  ____   ____   ____   ___________
/    \  \/ /  _ \ /    \ /    \ /  _ \_  __ \
\     \___(  <_> )   |  \   |  (  <_> )  | \/
 \______  /\____/|___|  /___|  /\____/|__|
        \/            \/     \/

just fyi i didnt make that
"""
