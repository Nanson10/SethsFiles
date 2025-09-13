import matplotlib.pyplot as plt
import numpy as np
import math
import time

#This version ignores rolling momentum due to the minor amount of energy it has
#This also simplifies calculations greatly

#Car Definitions
DRAGCOEF = .1    # Constant (Lux:0.1m^2)
FRONTAREA = 1.163  # m^2    (Lux:1.163m^2)

HUMIDITY = 0.5     # % 0-1
TEMPERATURE = 27   # Deg C

WHEELDIA = .5588   # m
MOTORDIA = .262    # m
ROLL_RESIST_COEF = .0025 #Constant  (Lux: .005)
TIMESTEP = 1       # Seconds
PACKMAXV = 115     # Volts
MOTORMAXA = 30     # Amps
ALTITUDE = 1000    # meters above sea level

PI = 3.1415        # Constant
GRAVITY = 9.81     #m/s^2
WEIGHT = 260       # kg
ELECTRICALEFF = 0.7 # % 0-1

ESTIMATED_BOARDS_POWER = 20 # Watts

wheel_circ = PI * WHEELDIA
rolling_resistance = ROLL_RESIST_COEF * WEIGHT * GRAVITY #Newtons

#------Read In Files------#
map_data = np.genfromtxt(r"C:\Users\schae\Documents\Purdue_Solar_Racing\Calculation_Tool\Coords2.txt", dtype=float, encoding=None)

#------ Barametric Formula------#
def find_pressure(elevation, temp):
    g = 9.80665 # Gravity
    m_air = 0.0289644 # kg/mol Molar Mass of air
    R = 8.31432 # Universal Gas constant
    P0 = 101325 # Pressure at Sea Level

    P = P0 * (math.e ** ((-1 * g * m_air * elevation) / (R * (temp + 273.15))))

    return P

#------ Humid Air Density ------#
# Created using https://en.wikipedia.org/wiki/Density_of_air
def humid_air(elevation, humidity, temp):
    pressure = find_pressure(elevation, temp)
    R_d = 287.058 # Specific gas constant for dry air
    R_v = 461.495 # Specific gas constant for water vapor

    p_sat = 6.1078 * (10 ** ((7.5 * temp) / (temp + 237.3)))
    p_water_vapor = humidity * p_sat

    p_dry_air = pressure - p_water_vapor

    temp += 273.15
    density = p_dry_air / (R_d * temp) + p_water_vapor / (R_v * temp)

    return density

#------ Drag Force ------#
def drag_force(velocity, elevation):
    
    density = humid_air(elevation, HUMIDITY, TEMPERATURE)
    drag = 0.5 * density * (velocity ** 2) * DRAGCOEF * FRONTAREA # Newtons

    return drag

def max_acceleration(desired_velocity, current_velocity):
    current_rpm = (current_velocity * 60) / wheel_circ   # RPM
    current_energy = .5 * WEIGHT * current_velocity**2   # Joules

    kinetic_energy_goal = 0.5 * WEIGHT * desired_velocity ** 2

    elapsed_time = 0
    distance_covered = 0
    distance_covered_tot = 0
    energy_consumed = 0
    energy_input = 0

    while(kinetic_energy_goal > current_energy):
        #Model is not perfect, jumps over the incorrect portion
        if current_rpm == 0:
            current_rpm += 5

        #Output Power Curve  (W)
        energy_input = (-1.0155 * 10**-13 * current_rpm**6) + (3.9602 * 10 **-10 * current_rpm**5) + (-6.2748 * 10**-7 * current_rpm**4) + (0.000527736 * current_rpm**3) + (-0.262281 * current_rpm**2) + (67.9487 * current_rpm) - 160.79 

        #Distance Covered total
        distance_covered_tot += current_rpm / 60 * TIMESTEP * wheel_circ #Meters
        #Distance Covered in previous step
        distance_covered = current_rpm / 60 * TIMESTEP * wheel_circ #Meters

        #Effeciency Curve (%)
        efficency = (-8.0242028 * 10**-30 * current_rpm**12) + (4.722082 * 10**-26 * current_rpm**11) + (-1.2160426 * 10**-22 * current_rpm**10) + (1.8000174 * 10**-19 * current_rpm**9) + (-1.6916303 * 10**-16 * current_rpm**8) + (1.0522394 * 10**-13 * current_rpm**7) + (-4.3820718 * 10**-11 * current_rpm**6) + (1.2087515 * 10**-8 * current_rpm**5) + (-0.00000213598103 * current_rpm**4) + (0.000226477763 * current_rpm**3) + (-0.012658382 * current_rpm**2) + (0.423810481 * current_rpm) -2.56006471

        energy_gain = energy_input * TIMESTEP #Joules

        #Sets a hard limit at 
        if energy_gain > (MOTORMAXA * PACKMAXV) * TIMESTEP:
            energy_gain = (MOTORMAXA * PACKMAXV) * TIMESTEP #Joules

        drag = drag_force(current_velocity, ALTITUDE)

        current_energy += (energy_gain * ELECTRICALEFF - ((drag + rolling_resistance) * distance_covered)) #Joules

        energy_consumed += energy_gain * (efficency / 100) #Joules

        current_velocity = (current_energy / (0.5 * WEIGHT))**.5 #m/s
    
        current_rpm = (current_velocity * 60) / wheel_circ   #RPM
        elapsed_time = elapsed_time + 1

        #print(current_velocity)

    elapsed_time = elapsed_time * TIMESTEP #Seconds
    energy_consumed = energy_consumed / 3600 #Watt/hours

    return energy_consumed


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

def route_calc(start_pos, end_pos, turns, speed):
    total_energy_lost = 0
    total_distance_traveled = 0
    total_time = 0

    current_rpm = (speed * 60) / wheel_circ   # RPM
    efficency = (-8.0242028 * 10**-30 * current_rpm**12) + (4.722082 * 10**-26 * current_rpm**11) + (-1.2160426 * 10**-22 * current_rpm**10) + (1.8000174 * 10**-19 * current_rpm**9) + (-1.6916303 * 10**-16 * current_rpm**8) + (1.0522394 * 10**-13 * current_rpm**7) + (-4.3820718 * 10**-11 * current_rpm**6) + (1.2087515 * 10**-8 * current_rpm**5) + (-0.00000213598103 * current_rpm**4) + (0.000226477763 * current_rpm**3) + (-0.012658382 * current_rpm**2) + (0.423810481 * current_rpm) -2.56006471

    #print(efficency)

    for x in range(start_pos, end_pos):
        horizontal_delta = lat_long_to_meters(map_data[x, 0], map_data[x,1], map_data[x+1, 0], map_data[x+1,1])

        elevation_change = map_data[x+1, 2] - map_data[x, 2]
        vertical_delta = elevation_change * WEIGHT * GRAVITY #Energy used for elevation change in joules

        distance_traveled = math.sqrt(horizontal_delta**2 + elevation_change**2)
        time_taken = distance_traveled / speed
        if time_taken == 0:
            time_taken = .001

        rolling_resistance_work = rolling_resistance * distance_traveled #Work joules
        drag = drag_force(speed, (map_data[x+1, 2] + vertical_delta / 2))
        rolling_energy = rolling_resistance_work / time_taken
        drag_energy = (drag * distance_traveled) / time_taken

        vertial_energy = vertical_delta / time_taken

        total_energy_lost += ((rolling_energy + drag_energy) * (1/ELECTRICALEFF) * (1/(efficency/100)) + vertial_energy) #Watt-Hours
        total_distance_traveled += distance_traveled
        total_time += time_taken

        # print('Distance: ' + str(total_distance_traveled) + '   Energy: ' + str(total_energy_lost / 3600) + '   Time: ' + str(total_time))


    total_energy_lost /= 3600 #Convert from watt-seconds to watt-hours
    total_time /= 3600 #Convert from seconds to hours

    total_energy_lost += max_acceleration(speed, 0) * turns
    total_energy_lost += ESTIMATED_BOARDS_POWER * (total_time)

    print(str(total_energy_lost) + (' watt-hours consumed'))
    print(str(total_distance_traveled /1609) + (' distance traveled (miles)'))
    print(str(total_time) + ('Hours'))
    print(str((total_distance_traveled / 1609) / (total_energy_lost / 33700)) + ' MPGe')
    print("")

def do_it(speed):
    #Start Point, End Point, Turns
    # print("Nashville - Paducah")
    # route_calc(0, 4688, 24, speed)      #Step 1 Nashville - Paducah (0-4688)

    # print("Paducah")
    # route_calc(4689, 6198, 9, speed)    #Loop 1 Paducah (4689-6198)

    # print("Paducah - Edwardsville")
    # route_calc(6199, 11033, 32, speed)  #Step 2 Paducah - Edwardsville (6199-11033)

    # print("Edwardsville")
    # route_calc(11034, 12091, 14, speed)  #Loop 2 Edwardsville (11034-12091)

    # print("Edwardsville - Jefferson City")
    # route_calc(12092, 17146, 19, speed)  #Step 3 Edwardsville - Jefferson City (12092-17146)

    # print("Jefferson City")
    # route_calc(17147, 17927, 13, speed)  #Loop 3 Jefferson City (17147-17927)

    # print("Jefferson City - Independence")
    # route_calc(17928, 21391, 15, speed)  #Step 4 Jefferson City - Independence (17928-21391)

    # print("Independence - St.Joseph")
    # route_calc(21392, 23242, 15, speed)  #Step 5 Independence - St.Joseph (21392-23242)

    # print("St. Joseph")
    # route_calc(23243, 23898, 4, speed)   #Loop 4 St.Joseph (23243-23898)

    # print("St.Joseph - Beatrice")
    # route_calc(23899, 25513, 6, speed)   #Step 6 St.Joseph - Beatrice (23899-25513)

    # print("Beatrice")
    # route_calc(25514, 26083, 11, speed)  #Loop 5 Beatrice (25514-26083)

    # print("Beatrice - Kearney")
    # route_calc(26084, 27846, 16, speed)  #Step 7 Beatrice - Kearney (26084-27846)

    # print("Kearney")
    # route_calc(27847, 28412, 8, speed)   #Loop 6 Kearney (27847-28412)

    # print("Kearney - Gearing")
    # route_calc(28413, 32117, 11, speed)  #Step 8 Kearney - Gearing (28413-32117)

    # print("Gearing")
    # route_calc(32118, 32740, 9, speed)   #Loop 7 Gearing (32118-32740)

    # print("Gearing - Casper")
    # route_calc(32741, 35984, 17, speed)  #Step 9 Gearing - Casper (32741-35984)

    print("Fitting")
    route_calc(33916, 35984, 17, speed) 

    

do_it(13.4)