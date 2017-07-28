import numpy as np

def new_cord(lat_x, lon_y, a_z):
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

        start=start+1

    f = interpolate.Rbf(lat_x, lon_y, a_z, smooth=2)

    new_lat = (float(lat_1+lat_2)/2)

    new_lon = (float(lon_1+lon_2)/2)

    print new_lat, new_lon

    new_a =  f(new_lat, new_lon)

    print new_a

    lat = np.append(lat_x, new_lat)
    lon = np.append(lon_y, new_lon)
    a = np.append(a_z, new_a)
