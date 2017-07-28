import numpy as np

def new_cord(lat, lon, a):
    cord_sample = random.sample(zip(lat,lon), 2)

    lat_1 = (float(cord_sample[0][0]))
    lon_1 = (float(cord_sample[0][1]))
    lat_2 = (float(cord_sample[1][0]))
    lon_2 = (float(cord_sample[1][1]))

    f = interpolate.Rbf(lon, lat, a, smooth=2)

    new_lat = (float(lat_1+lat_2)/2)

    new_lon = (float(lon_1+lon_2)/2)


    new_a =  f(new_lat, new_lon)


    lat = np.append(lat, new_lat)
    lon = np.append(lon, new_lon)
    a = np.append(a, new_a)
