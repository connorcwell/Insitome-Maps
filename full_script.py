print "Loading..."
import time
start = time.time()
import folium
from folium import plugins
import pandas as pd
import numpy as np
from numpy import genfromtxt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import scipy
from scipy import interpolate
from scipy.interpolate import Rbf
from math import cos, asin, sqrt
from functools import partial

name = raw_input("What's your name? ")
print "How are you %s?" % name
how = raw_input("")

if how != "Bad" and how != "Terrible" and how != "Not so Good" and how != "Eh":
    print "Glad to hear that %s! Why don't we get on with the program then." % name
else:
    print "Sorry to hear that %s. Let's get on with the program." % name

def getClosest(array, coord):
    dist=lambda s,d: (s[0]-d[0])**2+(s[1]-d[1])**2 #a little function which calculates the distance between two coordinates
    clos =  min(array, key=partial(dist, coord))
    dat = np.delete(array, np.where(array == clos), axis=0)
    clos_new =  min(dat, key=partial(dist, coord))
    dat_new = np.delete(array, np.where(array == clos_new), axis=0)
    clos_new_1 = min(dat_new, key=partial(dist, coord))
    return np.concatenate((clos_new,clos_new_1))

def distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    Source: https://gis.stackexchange.com/a/56589/15183
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km

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

def main(dataset, lat_x, lon_y, a_z, smooth, nb_points):
    """
    returns an array of midpoints (main function)

    """
    if nb_points > 0:
        start = 0
        end=len(dataset)
        new_cords = np.array([]) #creates empty numpy array for data to append to
        while (start < end):
            lat_1=(dataset[start][0]) #loops through original cords
            lon_1=(dataset[start][1])
            start2 = 0
            while (start2 < end):
                lat_2=(dataset[start2][0]) #loops through again to get a pair of two cords
                lon_2=(dataset[start2][1])
                start2=start2+1
                start3 = 0

                while (start3 < end):
                    interm = intermediates(lat_1,lon_1,lat_2,lon_2,nb_points) #determines intermediates
                    interm = np.array(interm) #converts intermediates to numpy array
                    new_lat = [float(item[0]) for item in interm] #seperates lat
                    new_lon = [float(item[1]) for item in interm] #seperates lon
                    f = interpolate.Rbf(lat_x, lon_y, a_z, smooth=smooth) #creates interpolation method

                    new_a =  f(new_lat, new_lon) #generates new allele freq using interpolation function
                    new_set = (zip(new_lat,new_lon,new_a)) #zips each lat lon and allele freq together
                    new_set_1 = np.array(new_set) #converts the zipped data into a numpy array
                    new_cords =  np.append(new_cords,new_set_1) #appends the data to an empty numpy array
                    start3=start3+1
            start=start+1
            n = len(new_cords)/3 #determines length of numpy array
        return np.reshape(new_cords, (n,3)) #reshapes numpy array for future merging
    else:
        print "Error in arg nb_points: Need to enter value greater than 0"

def getData():
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

    #merging data onto one database
    flt = pd.merge(cord, al, copy=False, on='CODE')

    res = pd.merge(flt, trait, copy=False, on='RS')

    full = pd.merge(res, pop, copy=False, on='CODE')

    #converts cordinate and allele data to numpy array
    array = flt.as_matrix()
    return array

def render(number_points, smoothing, radius, array):
    #takes numpy array and turns data into values to go on map
    lat = [float(item[1]) for item in array] #isolates lat from the main numpy array
    lon = [float(item[2]) for item in array] #isolates lon
    a = [float(item[3]) for item in array] #isolates the allele freq

    real_zip = (zip(lat, lon)) #creates list that only has lat and lon to be used in function getPoints
    real = np.array(real_zip) #converts the list to numpy array so the lat and lon can be accessed
    old_data = (zip(lat,lon,a))
    dataset = np.array(real_zip)

    new_data = main(dataset,lat,lon,a,smoothing,number_points) #second to last arg is smoothing, arg after that is number of points in between

    data_cord = np.concatenate((old_data,new_data)) #merges the original set of cordinates and the interpolated cordinates

    #replace stamentoner with whatever tileset is best (custom ones can be made)
    m = folium.Map([48., 5.], tiles='stamentoner',control_scale = True, zoom_start=1)

    #play around with radius value to see which one is best, and gradient changes heatmap colors
    m.add_child(plugins.HeatMap(data_cord, radius = radius, gradient={.1: 'blue', .2: 'green', .3: 'orange', .5: 'red', .7: 'white'}))

    m.save('map.html') #saves map as html file

if __name__ == "__main__":
    number_points = input("How many points do you want in between? ")
    if number_points > 25:
        print "That's too big of a number!"
    else:
        print "Alrighty!"

    smoothing = input("What would you like the smoothing to be? ")

    print "Sure!"

    radius = input("What do you want the radius to be? ")

    print "No problem!"

    print "Wait a sec..."

    ar = getData()
    render(number_points, smoothing, radius, ar)


    print "Before I can give you the map you must enter your credit card number!"
    credit_card = input("Enter credit card number here: ")
    print "Hahaha just kidding! But if you actually entered your credit card then thanks!"
    print "Let's continue shall we?"


endTime = time.time()-start

print 'Finished the map in', endTime, 'seconds!'

print "kind of created by Connor Caldwell"

"""
_________
\_   ___ \  ____   ____   ____   ___________
/    \  \/ /  _ \ /    \ /    \ /  _ \_  __ \
\     \___(  <_> )   |  \   |  (  <_> )  | \/
 \______  /\____/|___|  /___|  /\____/|__|
        \/            \/     \/
"""
