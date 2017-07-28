import numpy as np

def new_cord(lat_x, lon_y, a_z):
    start = 0
    end=len(real)   #loops through cordinate data array
    while (start < end):
        lat_1=(real[start][0])  #gets a lat to generate mid point
        lon_1=(real[start][1])  #gets a lon to generate mid point
        start2 = 0
        while (start2 < end):
            lat_2=(real[start2][0]) #second lat to gen mid point the [0] is for column 1
            lon_2=(real[start2][1]) #second lon to gen mid point the [1] is for column 2 in the data
            start2=start2+1

        start=start+1

    f = interpolate.Rbf(lat_x, lon_y, a_z, smooth=2)    #creates an interpolated allele frequency based on current lat, lon, and allele freq

    new_lat = (float(lat_1+lat_2)/2)    #uses mid-point formula to gen mid point lat

    new_lon = (float(lon_1+lon_2)/2)    #mid-point formula to gen mid point lon

    print new_lat, new_lon  

    new_a =  f(new_lat, new_lon)    #using interpolating to gen allele freq for midpoint

    print new_a

    lat = np.append(lat_x, new_lat) #merges mid point lat to main lat data
    lon = np.append(lon_y, new_lon) #merges mid point lon to main lon data
    a = np.append(a_z, new_a)   #merges mid point allele freq to main allele data
