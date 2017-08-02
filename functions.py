import numpy as np

def intermediates(lat_1, lon_1, lat_2, lon_2, nb_points):
    """"Return a list of nb_points equally spaced points
    between p1 and p2"""
    # If we have 8 intermediate points, we have 8+1=9 spaces
    # between p1 and p2
    x_spacing = (lat_2 - lat_1) / (nb_points + 1)
    y_spacing = (lon_2 - lon_1) / (nb_points + 1)

    return [[lat_1 + i * x_spacing, lon_1 +  i * y_spacing]
            for i in range(1, nb_points+1)]

def getPoints(lat_x, lon_y, a_z, smooth, nb_points):
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
                while (start3 < end):
                    interm = intermediates(lat_1,lon_1,lat_2,lon_2,nb_points)
                    interm = np.array(interm)
                    new_lat = [float(item[0]) for item in interm]
                    new_lon = [float(item[1]) for item in interm]
                    f = interpolate.Rbf(lat_x, lon_y, a_z, smooth=smooth)

                    new_a =  f(new_lat, new_lon)

                    new_cords = (zip(new_lat,new_lon,new_a))
                    new_cords = np.array(new_cords)
                    start3=start3+1

            start=start+1
    else:
        print "Error in arg nb_points: Need to enter value greater than 0"
return new_cords
