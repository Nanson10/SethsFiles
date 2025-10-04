import matplotlib.pyplot as plt
import numpy as np
import math
import time

#
# The Lord and Savior https://www.researchgate.net/figure/Torque-versus-speed_fig20_350787435#
#Constants
WEIGHT = 260         #Car Weight (kg)
wheel_dia = 0.558    #Wheel diameter (m) .66
motor_dia = 0.262    #Motor diameter (m)
pi = 3.1415          #PI
rpm_min = 60
rpm_max = 100
temp = 27          #Degrees C
humidity = .5       #Humidity Percentage
wheel_weight = 4.670 #kg
motor_weight = 10.413 #kg
GRAVITY = 9.81

accelerations = [21, 9, 7]

speed_to_maintain = 21 #speed in m/s

ROLL_RESISTANCE_COEFF = .005
ROLLING_RESISTANCE = ROLL_RESISTANCE_COEFF * WEIGHT * GRAVITY

battery_count = 290  #Count
battery_volt = 4.2   #Max Voltage
battery_cap = 5000   #mAh
overall_efficiency = 0.95

RADIOS = 5
DISPLAYS = 3
RAS_PI = 10
PERFERIAL = 5
LIGHTS = 10
CAMERA = 5
TELEMETRY = 3
HORN = 5
ESTIMATED_BOARDS_POWER = RADIOS + DISPLAYS + RAS_PI + PERFERIAL + LIGHTS + CAMERA + TELEMETRY + HORN

#Effeciency Curve X is RMP R = .9954
#Y = (-9.4216 * 10**-25 * x**10) + (4.6085 * 10**-21 * x**9) + (-9.6036 * 10**-18 * x**8) + (1.1121 * 10**-14 * x**7) + (-7.8285 * 10**-12 * x**6) + (3.4434 * 10**-9 * x**5) + (-9.3664 * 10**-7 * x**4) + (0.000150044 * x**3) + (-0.012685 * x**2) + (0.596489 * x) -5.75449
#Output Power in watts R=1
#Y = (-1.0155 * 10**-13 * x**6) + (3.9602 * 10 **-10 * x**5) + (-6.2748 * 10**-7 * x**4) + (0.000527736 * x**3) + (-0.262281 * x**2) + (67.9487 * x) - 160.79
#Torque Curve
#Y = (-1 * x**6) + (0.0023 * x**2) + -1.875 * x + 598.9

#------Read In Files------#
map_data = np.genfromtxt(r"./Coords2.txt", dtype=float, encoding=None)

#------Power Estimations------#
watt_hours = battery_volt * battery_cap * battery_count / 1000
watt_hours *= overall_efficiency


#------ Barametric Formula------#
def find_pressure(height, temp):
    g = 9.80665 # Gravity
    m_air = 0.0289644 # kg/mol Molar Mass of air
    R = 8.31432 # Universal Gas constant
    P0 = 101325 # Pressure at Sea Level

    P = P0 * (math.e ** ((-1 * g * m_air * height) / (R * (temp + 273.15))))

    return P

#------ Humid Air Density ------#
# Created using https://en.wikipedia.org/wiki/Density_of_air
def humid_air(height, humidity, temp):
    pressure = find_pressure(height, temp)
    R_d = 287.058 # Specific gas constant for dry air
    R_v = 461.495 # Specific gas constant for water vapor

    p_sat = 6.1078 * (10 ** ((7.5 * temp) / (temp + 237.3)))
    p_water_vapor = humidity * p_sat

    p_dry_air = pressure - p_water_vapor

    temp += 273.15
    density = p_dry_air / (R_d * temp) + p_water_vapor / (R_v * temp)

    return density


#------ Drag Force ------#
def drag_force(velocity, height):
    drag_coeff = .1
    frontal_area = 1.163  #m^2 Actual:1.163
    density = humid_air(height, humidity, temp)

    drag = 0.5 * density * (velocity ** 2) * drag_coeff * frontal_area # Newtons

    return drag

#------ Inverse Energy Function ------#
#Fuck the real math
# rotational_energy = []
# std_kinetic_energy = []

# for i in range(0, 4400, 1):
#     i /= 100
#     rpm_required = i / (2 * pi * (wheel_dia / 2))
#     rotational_energy.append(0.5 * ((3 * wheel_weight * (wheel_dia / 2)**2) + (motor_weight * (motor_dia / 2)**2)) * rpm_required ** 2)
#     std_kinetic_energy.append(0.5 * weight * i ** 2)

# sourcefile = open('rotational_energy.txt', 'w')
# for i in range(0, 4400, 1):
#     print(rotational_energy[i], file = sourcefile)
# sourcefile.close()

# sourcefile = open('kinetic_energy.txt', 'w')
# for i in range(0, 4400, 1):
#     print(std_kinetic_energy[i], file = sourcefile)
# sourcefile.close()

#------ Find Energy Used for Speed -----#
def energy_used(current_velocity, energy_input, drag, time_step):

    current_rpm = (current_velocity * 60) / ( (2 * pi * (wheel_dia / 2)))
    drag *= time_step
    energy_input += drag

    #Splits rotational and forward momentum
    energy_consumed_percernet = (-9.4216 * 10**-25 * current_rpm**10) + (4.6085 * 10**-21 * current_rpm**9) + (-9.6036 * 10**-18 * current_rpm**8) + (1.1121 * 10**-14 * current_rpm**7) + (-7.8285 * 10**-12 * current_rpm**6) + (3.4434 * 10**-9 * current_rpm**5) + (-9.3664 * 10**-7 * current_rpm**4) + (0.000150044 * current_rpm**3) + (-0.012685 * current_rpm**2) + (0.596489 * current_rpm) -5.75449

    energy_consumed_percernet = 1 / (energy_consumed_percernet / 100)
    energy_consumed = energy_consumed_percernet * energy_input #Kw
    energy_consumed *= (time_step / 3600) #Kwh

    return energy_consumed

#------ Acceleration ------#
# The code works, don't touch it
def max_acceleration(desired_velocity, current_velocity):
    rpm_required = (desired_velocity * 60) / ( (2 * pi * (wheel_dia / 2)))
    current_rpm = (current_velocity * 60) / ( (2 * pi * (wheel_dia / 2)))

    rotational_energy = 0.5 * ((3 * wheel_weight * (wheel_dia / 2)**2) + (motor_weight * (motor_dia / 2)**2)) * rpm_required ** 2
    std_kinetic_energy = 0.5 * WEIGHT * desired_velocity ** 2

    energy_needed = rotational_energy + std_kinetic_energy
    
    times = 0
    current_energy = 0
    time_step = .1
    energy_consumed = 0
    distance_covered = 0

    speed = []
    steps = []

    while(energy_needed > current_energy):   #or energy_needed > current_energy
        if current_rpm == 0:
            current_rpm += 5
        
        energy_input = (-1.0155 * 10**-13 * current_rpm**6) + (3.9602 * 10 **-10 * current_rpm**5) + (-6.2748 * 10**-7 * current_rpm**4) + (0.000527736 * current_rpm**3) + (-0.262281 * current_rpm**2) + (67.9487 * current_rpm) - 160.79

        if (energy_input < 0):
            energy_input = 0.1
        
        distance_covered += current_rpm / 60 * time_step * pi * wheel_dia
        
        #Uses ratios of rotational energy and linear energy to solve for current velocity
        #Only valid for current weights and wheel diameters
        #Solve for a,b, and c by adding rotational and kinetic, then find polynomial fit
        a = 1130.2064066
        b = 0
        c = 0 - current_energy

        dis = (b**2) - (4*a*c)
        current_velocity = (-b+math.sqrt(abs(dis)))/(2 * a)
        current_rpm = (current_velocity * 60) / (2 * pi * (wheel_dia / 2))

        current_energy += (energy_input * time_step)

        drag = drag_force(current_velocity, 1000)
        rolling_resistance_work = current_velocity * ROLLING_RESISTANCE
        current_energy -= ((drag + rolling_resistance_work) * time_step)

        # speed.append(current_velocity)
        # steps.append(times)

        energy_consumed += energy_used(current_velocity, energy_input, drag, time_step)

        times += time_step
        if(current_velocity > desired_velocity):
            break
    
    # plt.plot(steps, speed)
    # plt.xlabel('Time (Seconds)')
    # plt.ylabel('Velocity (m/s)')
    # plt.show()

    # print(str(energy_consumed) + " watt-hours")
    # print(str(distance_covered) + " Meters")

    return(energy_consumed)


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
    #Slow Speed is 30mph, fast speed is 50mph, for now use 50mph for everything
    #total_miles = 153
    #fast_miles = 149
    total_energy_lost = 0
    total_distance_traveled = 0
    total_time = 0

    for x in range(start_pos, end_pos):
        horizontal_delta = lat_long_to_meters(map_data[x, 0], map_data[x,1], map_data[x+1, 0], map_data[x+1,1])

        elevation_change = map_data[x+1, 2] - map_data[x, 2]
        vertical_delta = elevation_change * WEIGHT * GRAVITY #Energy used for elevation change in joules

        distance_traveled = math.sqrt(horizontal_delta**2 + elevation_change**2)
        time_taken = distance_traveled / speed
        if time_taken == 0:
            time_taken = .001

        rolling_resistance_work = ROLLING_RESISTANCE * distance_traveled #Work joules
        drag = drag_force(speed, (map_data[x+1, 2] + vertical_delta / 2))
        rolling_energy = rolling_resistance_work / time_taken
        drag_energy = (drag * distance_traveled) / time_taken

        vertial_energy = vertical_delta / time_taken

        total_energy_lost += (rolling_energy + drag_energy + vertial_energy) #Watt-Hours
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
    print("")

    sourceFile = r"./Route1.txt"
    with open(sourceFile, 'a') as file:
        file.write(str(speed) + '\t' + str(total_energy_lost) + '\t' + str(total_time) + '\n')




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

    print("Gearing - Casper")
    route_calc(32741, 35984, 17, speed)  #Step 9 Gearing - Casper (32741-35984)

    
def many_speeds():
    for i in range(1, 30):
        do_it(i)
    
do_it(13.5)




    