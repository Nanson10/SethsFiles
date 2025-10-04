import matplotlib.pyplot as plt
import numpy as np
import math
import time

#------Read In Files------#
map_data = np.genfromtxt(r"./Coords2.txt", dtype=float, encoding=None)

def lat_long_to_meters(lat1, long1, lat2, long2):

    earth_radius = 6371000 #meters radius of earth

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(long1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(long2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = earth_radius * c

    # print("lat1 " + str(lat1) + " long1 " + str(long1) + " lat2 " + str(lat2) + " long2 " + str(long2))
    # print("distance: " + str(distance))

    return distance

def find_dist(start_pos, distance):
    total_distance_traveled = 0
    x = start_pos

    #print(efficency)

    while total_distance_traveled < distance:
        horizontal_delta = lat_long_to_meters(map_data[x, 0], map_data[x,1], map_data[x+1, 0], map_data[x+1,1])

        elevation_change = map_data[x+1, 2] - map_data[x, 2]

        distance_traveled = math.sqrt(horizontal_delta**2 + elevation_change**2)

        total_distance_traveled += distance_traveled
        x += 1


    print(str(total_distance_traveled /1609) + (' distance traveled (miles)'))
    print("")