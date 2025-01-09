from api.metadata.metadata import set_gps_coordinates, read_gps_coordinates

path = "./uploads/drone/vague1/1736197996_brownspot_orig_003.jpg"
set_gps_coordinates(path, 48.858844, 2.294351)
read_gps_coordinates(path)