import matplotlib.pyplot as plt
import numpy as np
import math
import time

plt.style.use('dark_background')


# This version ignores rolling momentum due to the minor amount of energy it has
# This also simplifies calculations greatly

# Car Definitions
DRAG_COEFF = 0.16                # Constant (Lux:0.1m^2)
FRONT_AREA = 1.163              # m^2    (Lux:1.163m^2)

HUMIDITY = 0.5                  # % 0-1
TEMPERATURE = 27                # Deg C

WHEEL_DIA = .5588               # m  (Lux .5588)
MOTOR_DIA = .262                # m  (Lux .262)
ROLL_RESIST_COEFF = .0025       # Constant  (Lux: .0025)
TIMESTEP = 1                    # Seconds
MAX_PACK_V = 115                # Volts
MAX_MOTOR_A = 30                # Amps
ALTITUDE = 1000                 # meters above sea level

PI = 3.1415                     # Constant
GRAVITY = 9.80665               # m/s^2
MASS = 1500                      # kg (Lux 260kg)
ELECTRICAL_EFF = 0.8            # % 0-1
SECONDS_TO_HOURS = 3600         # Conversion factor

ESTIMATED_BOARDS_POWER = 50     # Watts

WHEEL_CIRC = PI * WHEEL_DIA     # M
ROLLING_RESISTANCE = ROLL_RESIST_COEFF * MASS * GRAVITY # Newtons

# list1 = list(range(1,15000))
# points = list(range(1,15000))
# list2 = list(range(0,35984))
# list3 = list(range(0,35984))


#------Read In Files------#
map_data = np.genfromtxt(r"./Coords2.txt", dtype=float, encoding=None)


#------ Barometric Formula------#
def find_pressure(elevation: float, temp: float) -> float:
    """
    Finds the pressure at an elevation above sea level

    Args:
        elevation (float): Height above sea level (m)
        temp (float): Temperature (degrees C)

    Returns:
        float: Pressure at the requested elevation level (Pa)
    """
    m_air = 0.0289644       # kg/mol Molar Mass of air
    R = 8.31432             # Universal Gas constant
    P0 = 101325             # Pressure at Sea Level

    return P0 * (math.e ** ((-1 * GRAVITY * m_air * elevation) / (R * (temp + 273.15))))


#------ Humid Air Density ------#
# Created using https://en.wikipedia.org/wiki/Density_of_air
def humid_air(elevation: float, humidity: float, temp: float) -> float:
    """
    Calculates the density of air at a given
    altitude depending on relative humidity

    Args:
        elevation (float): Height above sea level (m)
        humidity (float): Relative Humidity (0-1)
        temp (float): Temperature (degrees C)

    Returns:
        float: Density of humid air at specified altitude
    """
    pressure = find_pressure(elevation, temp)                      # Pressure at altitude (Pa)
    R_d = 287.058                                                  # Specific gas constant for dry air (J/kg.K)
    R_v = 461.495                                                  # Specific gas constant for water vapor (J/kg.K)

    p_sat = 610.78 * (math.e ** ((17.27 * temp) / (temp + 237.3))) # Saturation Vapor Pressure (Pa)
    p_water_vapor = humidity * p_sat                               # Vapor Pressure of Water (Pa)

    p_dry_air = pressure - p_water_vapor

    temp += 273.15                                                 # Temperature (K)
    return p_dry_air / (R_d * temp) + p_water_vapor / (R_v * temp)


#------ Drag Force ------#
def drag_force(velocity: float, elevation: float) -> float:
    """
    Calculate the drag force at given altitude and velocity

    Args:
        velocity (float): Velocity (m/s)
        elevation (float): Altitude (m)

    Returns:
        float: The drag force acting on the object
    """
    density = humid_air(elevation, HUMIDITY, TEMPERATURE)
    return 0.5 * density * (velocity ** 2) * DRAG_COEFF * FRONT_AREA  # Newtons


# Might want to rename the function to energy_consumed
def max_acceleration(desired_velocity: float, current_velocity: float) -> float:
    """
    Calculate the energy consumed to increase speed from
    current_velocity to desired_velocity

    Args:
        desired_velocity (float): Final velocity (m/s)
        current_velocity (float): Initial velocity (m/s)

    Returns:
        float: Energy consumed (Wh)
    """
    current_rpm = (current_velocity * 60) / WHEEL_CIRC   # RPM
    current_energy = 0.5 * MASS * current_velocity**2   # Joules
    kinetic_energy_goal = 0.5 * MASS * desired_velocity ** 2

    elapsed_time = 0
    distance_covered = 0
    distance_covered_tot = 0
    energy_consumed = 0
    power_input = 0

    while kinetic_energy_goal > current_energy:
        # Model is not perfect, jumps over the incorrect portion
        if current_rpm == 0: current_rpm += 5

        # Output Power Curve  (W)
        power_input = (-1.0155 * 10**-13 * current_rpm**6) + (3.9602 * 10 **-10 * current_rpm**5) + (-6.2748 * 10**-7 * current_rpm**4) + (0.000527736 * current_rpm**3) + (-0.262281 * current_rpm**2) + (67.9487 * current_rpm) - 160.79

        # Distance Covered total
        distance_covered_tot += current_rpm / 60 * TIMESTEP * WHEEL_CIRC # Meters

        # Distance Covered in previous step
        distance_covered = current_rpm / 60 * TIMESTEP * WHEEL_CIRC # Meters

        # Effeciency Curve (%)
        efficency = (-8.0242028 * 10**-30 * current_rpm**12) + (4.722082 * 10**-26 * current_rpm**11) + (-1.2160426 * 10**-22 * current_rpm**10) + (1.8000174 * 10**-19 * current_rpm**9) + (-1.6916303 * 10**-16 * current_rpm**8) + (1.0522394 * 10**-13 * current_rpm**7) + (-4.3820718 * 10**-11 * current_rpm**6) + (1.2087515 * 10**-8 * current_rpm**5) + (-0.00000213598103 * current_rpm**4) + (0.000226477763 * current_rpm**3) + (-0.012658382 * current_rpm**2) + (0.423810481 * current_rpm) -2.56006471

        energy_gain = power_input * TIMESTEP # Joules
        # Sets a hard limit at the max power that can be delivered
        if energy_gain > (MAX_MOTOR_A * MAX_PACK_V) * TIMESTEP: energy_gain = (MAX_MOTOR_A * MAX_PACK_V) * TIMESTEP #Joules

        drag = drag_force(current_velocity, ALTITUDE)
        
        # Here, should ELECTRICAL_EFF or efficiency / 100 be used?
        current_energy += (energy_gain * ELECTRICAL_EFF - ((drag + ROLLING_RESISTANCE) * distance_covered)) # Joules
        energy_consumed += energy_gain * (efficency / 100) # Joules

        current_velocity = (current_energy / (0.5 * MASS))**0.5 # m/s
        current_rpm = (current_velocity * 60) / WHEEL_CIRC      # RPM
        elapsed_time = elapsed_time + 1

    elapsed_time *= TIMESTEP      # Seconds
    energy_consumed /= SECONDS_TO_HOURS    # Wh
    print(elapsed_time)
    return energy_consumed


# Trusting this function
def lat_long_to_meters(lat1: float, long1: float, lat2: float, long2: float) -> float:
    """
    Calculate the distance (in m) between the two given coordinates

    Args:
        lat1 (float): Latitude of coordinate 1
        long1 (float): Longitude of coordinate 1
        lat2 (float): Latitude of coordinate 2
        long2 (float): Longitude of coordinate 2

    Returns:
        float: Distance between the 2 points
    """

    earth_radius = 6371000 # radius of earth (m)

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(long1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(long2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius * c


def route_calc(start_pos: int, end_pos: int, turns: int, speed: float) -> None:
    """
    Run calculations to find total energy lost, total
    distance travelled and total time taken

    Args:
        start_pos (int): Integer indicating the start position
        end_pos (int): Integer indicating the end position
        turns (int): Number of turns (when the car comes to a stop?)
        speed (float): Starting speed (m/s)

    Notes:
        When calculating total_energy_lost on line 233, powers were being used; I changed this
    """

    total_energy_lost = 0
    total_distance_traveled = 0
    total_time = 0

    current_rpm = (speed * 60) / WHEEL_CIRC   # RPM
    efficency = (-8.0242028 * 10**-30 * current_rpm**12) + (4.722082 * 10**-26 * current_rpm**11) + (-1.2160426 * 10**-22 * current_rpm**10) + (1.8000174 * 10**-19 * current_rpm**9) + (-1.6916303 * 10**-16 * current_rpm**8) + (1.0522394 * 10**-13 * current_rpm**7) + (-4.3820718 * 10**-11 * current_rpm**6) + (1.2087515 * 10**-8 * current_rpm**5) + (-0.00000213598103 * current_rpm**4) + (0.000226477763 * current_rpm**3) + (-0.012658382 * current_rpm**2) + (0.423810481 * current_rpm) -2.56006471

    for x in range(start_pos, end_pos):
        horizontal_delta = lat_long_to_meters(map_data[x, 0], map_data[x,1], map_data[x+1, 0], map_data[x+1,1])

        elevation_change = map_data[x+1, 2] - map_data[x, 2]

        vertical_energy = elevation_change * MASS * GRAVITY #Energy used for elevation change in joules

        distance_traveled = math.sqrt(horizontal_delta**2 + elevation_change**2)
        time_taken = distance_traveled / speed
        if time_taken == 0: time_taken = .001

        ROLLING_RESISTANCE_work = ROLLING_RESISTANCE * distance_traveled #Work joules
        drag = drag_force(speed, (map_data[x+1, 2] + vertical_energy / 2))
        print(drag)
        print(distance_traveled)
        if drag / distance_traveled > 50:
            drag = 0
        rolling_energy_WH = ROLLING_RESISTANCE_work / SECONDS_TO_HOURS
        drag_energy_WH = (drag * distance_traveled) / SECONDS_TO_HOURS

        vertical_energy_WH = vertical_energy / SECONDS_TO_HOURS

        total_energy_lost += ((rolling_energy_WH + drag_energy_WH) * (1/ELECTRICAL_EFF) * (1/(efficency/100)) + vertical_energy_WH) #Watt-Hours
        total_distance_traveled += distance_traveled
        total_time += time_taken

        # list1[x] = total_energy_lost
        # list2[x] = total_time
        # list3[x] = total_distance_traveled

    total_time /= SECONDS_TO_HOURS # Convert from seconds to hours
    total_energy_lost += max_acceleration(speed, 0) * turns
    total_energy_lost += ESTIMATED_BOARDS_POWER * (total_time)

    print(str(total_energy_lost) + (' watt-hours consumed'))
    print(str(total_distance_traveled /1609) + (' distance traveled (miles)'))
    print(str(total_time) + (' Hours'))
    print(str((total_distance_traveled / 1609) / (total_energy_lost / 33700)) + ' MPGe')
    print("")


def main(speed: float) -> None:
    """
    Run the route_calc function for different legs of the race

    Args:
        speed (float): Starting speed
    """
    #Start Point, End Point, Turns
    # print("Nashville - Paducah")
    # route_calc(0, 4689, 24, speed)      #Step 1 Nashville - Paducah (0-4688)

    # print("Paducah")
    # route_calc(4689, 6199, 9, speed)    #Loop 1 Paducah (4689-6198)

    # print("Paducah - Edwardsville")
    # route_calc(6199, 11034, 32, speed)  #Step 2 Paducah - Edwardsville (6199-11033)

    # print("Edwardsville")
    # route_calc(11034, 12092, 14, speed)  #Loop 2 Edwardsville (11034-12091)

    # print("Edwardsville - Jefferson City")
    # route_calc(12092, 17147, 19, speed)  #Step 3 Edwardsville - Jefferson City (12092-17146)

    # print("Jefferson City")
    # route_calc(17147, 17928, 13, speed)  #Loop 3 Jefferson City (17147-17927)

    # print("Jefferson City - Independence")
    # route_calc(17928, 21392, 15, speed)  #Step 4 Jefferson City - Independence (17928-21391)

    # print("Independence - St.Joseph")
    # route_calc(21392, 23243, 15, speed)  #Step 5 Independence - St.Joseph (21392-23242)

    # print("St. Joseph")
    # route_calc(23243, 23899, 4, speed)   #Loop 4 St.Joseph (23243-23898)

    print("St.Joseph - Beatrice")
    route_calc(23899, 25514, 6, speed)   #Step 6 St.Joseph - Beatrice (23899-25513)

    # print("Beatrice")
    # route_calc(25514, 26084, 11, speed)  #Loop 5 Beatrice (25514-26083)

    # print("Beatrice - Kearney")
    # route_calc(26084, 27847, 16, speed)  #Step 7 Beatrice - Kearney (26084-27846)

    # print("Kearney")
    # route_calc(27847, 28413, 8, speed)   #Loop 6 Kearney (27847-28412)

    # print("Kearney - Gearing")
    # route_calc(28413, 32118, 11, speed)  #Step 8 Kearney - Gearing (28413-32117)

    # print("Gearing")
    # route_calc(32118, 32741, 9, speed)   #Loop 7 Gearing (32118-32740)

    # print("Gearing - Casper")
    # route_calc(32741, 35984, 17, speed)  #Step 9 Gearing - Casper (32741-35984)

    # print("Fitting")
    # route_calc(33916, 35984, 17, speed) 

    # print("Fitting")
    # route_calc(13770, 13771, 10, speed) 

    # plt.plot(points, list1)
    # plt.plot(points, list2)
    # plt.plot(points, list3)
    # plt.show()

    
if __name__ == "__main__":
    #main(20)
    max_acceleration(20, 0)