import data
import functions

#takes numpy array and turns data into values to go on map
lat = [float(item[1]) for item in array]
lon = [float(item[2]) for item in array]
a = [float(item[3]) for item in array]

new_cord(lat, lon, a)

#replace stamentoner with whatever tileset is best (custom ones can be made)
m = folium.Map([48., 5.], tiles='stamentoner',control_scale = True, zoom_start=1)

#play around with radius value to see which one is best, and gradient changes heatmap colors
m.add_child(plugins.HeatMap(zip(lat, lon, a), radius = 25, gradient={.4: 'dodgerblue', .6: 'blue', 1: 'blue'}))

print "created map"

print "saving map..."
#saves heatmap as an html file
m.save('map.html')

