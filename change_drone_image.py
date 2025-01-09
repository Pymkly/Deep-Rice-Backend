from api.metadata.metadata import set_gps_coordinates, read_gps_coordinates
import os

coordinates = [
    {'lat':47.53338590500164,'lon':-19.02109312929402},
    {'lat': 47.53340956769443, 'lon': -19.02139153349722},
    {'lat': 47.533422600552, 'lon': -19.02176705232004},
    {'lat': 47.53320720026259, 'lon': -19.02229457812771},
    {'lat': 47.53267646391384, 'lon': -19.02269036124715},
    {'lat': 47.53210965735358, 'lon': -19.02303468138268},
    {'lat': 47.53136146070562, 'lon': -19.02324118723395},
    {'lat': 47.53052386149219, 'lon': -19.02355392072832},
    {'lat': 47.52974938958431, 'lon': -19.02384751985072},
]

path = './uploads/drone/vague2'
items = os.listdir(path)
for i in range(len(items)):
    file_name = os.path.join(path, items[i])
    set_gps_coordinates(file_name, coordinates[i]['lat'], coordinates[i]['lon'])

for i in range(len(items)):
    file_name = os.path.join(path, items[i])
    read_gps_coordinates(file_name)