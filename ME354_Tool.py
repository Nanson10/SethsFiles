import math

#Material
ult_strength = 68 #Kpsi
yield_strength = 57 #Kpsi
PI = 3.1415


def torque_moment(torque_max, torque_min, moment_max, moment_min):
    t_m = (torque_max + torque_min) / 2
    t_a = abs((torque_max - torque_min) / 2)
    m_m = (moment_max + moment_min) / 2
    m_a = abs((moment_max - moment_min) / 2)

    print("T_m = " + str(t_m))
    print("T_a = " + str(t_a))
    print("M_m = " + str(m_m))
    print("M_a = " + str(m_a))

def s_eeee(dia):
    S_e_prime = .5 * ult_strength
    K_a = 2 * ult_strength ** -0.217
    if(dia == 0):
        K_b = 0.9
    else:
         K_b = 0.879 * dia ** -.107

    K_c = 1.0

    #Ignore K_d and K_e are just 1s
    s_e = S_e_prime * K_a * K_b * K_c

    return s_e

def check_yeild(sigma_a, sigma_m):
    saftey_factor = (yield_strength * 1000) / (sigma_a + sigma_m)

    return(saftey_factor)

def retain_ring(t_m, m_a, dia):
    #For 1.75" Shaft 2 (Exit)
    # k_t = 3.75
    # k_ts = 2.6
    # q = 0.65
    # q_t = 0.68
    #For 1.5" Shaft 1 (Exit)
    k_t = 3.75
    k_ts = 2.6
    q = 0.65
    q_t = 0.67
    # For 1.25" Shaft 1 (Entry)
    # k_t = 3.4
    # k_ts = 2.5
    # q = 0.60
    # q_t = 0.65
    #Unknown Size
    # k_t = 5.0
    # k_ts = 3.0
    # q = 1
    # q_t = 1

    k_f = 1 + q *(k_t - 1)
    k_fs = 1 + q_t *(k_ts - 1)

    sigma_a = (32 * m_a) / (PI * dia**3)
    tau_m = (16 * t_m) / (PI * dia**3)

    sigma_a_prime = (k_f * sigma_a)
    sigma_m_prime = (3 * (k_fs * tau_m) **2)**0.5

    n = ((sigma_a_prime / (s_eeee(dia) * 1000)) + (sigma_m_prime / (ult_strength * 1000))) ** -1

    print("Factor of Saftey: " + str(n))
    print("Yield Factor of Saftey: " + str(check_yeild(sigma_a_prime, sigma_m_prime)))

# retain_ring(2720, 338.37, 1.406)

def shoulder(t_m, m_a, dia):
    #Input shaft
    #r/d = 0.1 , D/d = 1.2
    # k_t = 1.625
    # k_ts = 1.35
    # q = 0.77
    # q_t = 0.82

    #Output shaft
    # r/d = 0.1 , D/d = 1.2 NEED UPDATED
    k_t = 1.65
    k_ts = 1.35
    q = 0.8
    q_t = 0.85

    k_f = 1 + q *(k_t - 1)
    k_fs = 1 + q_t *(k_ts - 1)

    sigma_a = (32 * m_a) / (PI * dia**3)
    tau_m = (16 * t_m) / (PI * dia**3)

    sigma_a_prime = (k_f * sigma_a)
    sigma_m_prime = (3 * (k_fs * tau_m) **2)**0.5

    n = ((sigma_a_prime / (s_eeee(dia) * 1000)) + (sigma_m_prime / (ult_strength * 1000))) ** -1

    print("Factor of Saftey: " + str(n))
    print("Yield Factor of Saftey: " + str(check_yeild(sigma_a_prime, sigma_m_prime)))

# shoulder(-2720, 179.66, 1)

def key(t_m, m_a, dia):
    k_t = 2.14
    k_ts = 3
    q = .60
    q_t = .65

    k_f = 1 + q *(k_t - 1)
    k_fs = 1 + q_t *(k_ts - 1)

    sigma_a = (32 * m_a) / (PI * dia**3)
    tau_m = (16 * t_m) / (PI * dia**3)

    sigma_a_prime = (k_f * sigma_a)
    sigma_m_prime = (3 * (k_fs * tau_m) **2)**0.5

    n = ((sigma_a_prime / (s_eeee(dia) * 1000)) + (sigma_m_prime / (ult_strength * 1000))) ** -1

    print("Factor of Saftey: " + str(n))
    print("Yield Factor of Saftey: " + str(check_yeild(sigma_a_prime, sigma_m_prime)))

# key(2720, 1141.41, 1.5) #Input shaft key

def de_Goodman(saftey_factor, m_a, t_m):
    k_f = 1.7
    k_fs = 1.5
    dia = 0

    prt_1 = (16 * saftey_factor) / PI
    prt_2 = (2 * k_f * m_a) / (s_eeee(dia) * 1000)
    prt_3 = ((3 * (k_fs * t_m)**2) **.5) / (ult_strength * 1000)

    solved_dia = (prt_1 * (prt_2 + prt_3)) ** (1/3)

    print("Diameter Required: " + str(solved_dia))

# de_Goodman(1.5, 1141.41, 2720)

def bearing(shaft_rpm, desired_load, ball_or_roller):
    desired_life = 15000 * 60 * shaft_rpm
    a_1 = 1 # 90% Reliability
    operating_life = 1000000 #Standard operating life

    load_rating_needed = (desired_load * desired_life ** (1 / ball_or_roller)) / (a_1 * operating_life ** (1 / ball_or_roller))

    print("Load Rating: " + str(load_rating_needed))

# bearing(4000, 597.54,10/3)

def min_pinion_teeth(teeth_type, angle, gear_ratio):
    pt_1 = (2 * teeth_type) / ((1 + 2 * gear_ratio) * math.sin(math.radians(angle))**2) 
    pt_2 = (gear_ratio + (gear_ratio**2 + (1 + 2 * gear_ratio) * (math.sin(math.radians(angle)))**2)**.5)
    pinion_teeth = pt_1 * pt_2

    print("Number of Pinion teeth: " + str(pinion_teeth))
    print("Number of Gear teeth: " + str(pinion_teeth * gear_ratio))

    print("Number of Pinion teeth (Rounded): " + str(math.ceil(pinion_teeth)))
    print("Number of Gear teeth(Rounded): " + str(math.ceil(pinion_teeth) * gear_ratio))

def pitch_line_velocity(gear_dia, speed):
    vel = PI*gear_dia*speed/12

    #Equation 13-34
    return (vel)

def tangential_load(horsepower, gear_dia, speed):
    load = 33000 * (horsepower / pitch_line_velocity(gear_dia, speed))

    #Equation 13-35
    # print(load)
    return(load)

def sigma_c():
    k_o = 1 #Uniform Uniform Figure 14.17
    k_s = 1 #Constant from Figure 14.17
    w_t = tangential_load(85, 12.8, 1000) #Equation 13-35
    k_v = 1.575 #Figure 14-9
    k_m = 1.36 #Equation 14-30
    d_p = 3.2  #Diameter Pinion
    f = 2.5    #Face Width
    c_f = 1    #Constant given Figure 14.17
    i = .1285  #Equation 14-23
    c_p = 2300 #Table 14-8 Steel Steel

    #Equation 14-16
    sigma__c = c_p * (w_t * k_o * k_v * k_s * (k_m / (d_p * f)) * (c_f / i))**.5

    # print(sigma__c)
    return(sigma__c)

def sigma():
    k_o = 1 #Uniform Uniform Figure 14.17
    k_s = 1 #Constant from Figure 14.17
    w_t = tangential_load(85, 3.2, 4000) #Equation 13-35
    k_v = 1.575 #Figure 14-9
    k_m = 1.36 #Equation 14-30
    f = 2.5 #Face Width 
    p_d = 5 # Example 14-1, d = N/P
    j = 0.27 #Figure 14-6
    k_b = 1 #Equation 14.40

    #Equation 14-15
    sigma__ = w_t * k_o * k_v * k_s * (p_d / f) * ((k_m * k_b)/ j)

    # print(sigma__)
    return(sigma__)

def keys(height, width, torque, length, shaft_dia):
    radius = shaft_dia / 2
    ultimate_strength_key = 64 #Kpsi  Table A-20
    yield_strength_key = 54    #Kpsi  Table A-20
    #Shear - Equation 5.21
    tau = torque / (radius * width * length)
    shear_factor_saftey = (0.577 * 1000 * yield_strength_key) / tau

    #Crush - Example 7-6
    sigma_key = torque / (radius * (height / 2) * length)
    crush_factor_saftey = (yield_strength_key * 1000) / sigma_key

    print("Shear Factor of Saftey: " + str(shear_factor_saftey))
    print("Crush Factor of Saftey: " + str(crush_factor_saftey))

def gear_factor_of_saftey():
    #Bending
    #y_n pinion = 0.9, Gear = 0.92
    s_t = 75000 #Table 14-3
    y_n = 0.92 #Figure 14-14
    k_t = 1 #14-15 k_t = 1 if Temp < 250F
    k_r = 1.25 #Table 14-10

    n_bend = ((s_t * y_n) / (k_t * k_r)) / sigma()

    #Wear
    #z_n pinion = 0.8, Gear = 0.9
    z_n = .9 #Figure 14-15
    k_t = 1 #14-15 k_t = 1 if Temp < 250F
    k_r = 1.25 #Table 14-10
    s_c = 175000 #Table 14-6 Nitrided Steel Grade 3
    c_h =  1 #If Pinion =1

    n_wear = ((s_c * z_n * c_h) / (k_t * k_r)) / sigma_c()

    print("Bending Factor of Saftey" + str(n_bend))
    print("Wear Factor of Saftey" + str(n_wear))

gear_factor_of_saftey()

#keys(3/16, .25, 1360, .75, 1.25) #1.25 Shaft - pinion
#keys(.25, 3/8, 5440, 1.75, 1.5) #1.5 Shaft - gear


#bearing(1000, 702.84, 10/3)
#shoulder(-2720, 179.66, 1.25)
# min_pinion_teeth(1, 20, 4)
# pitch_line_velocity(3.2, 4000)
# tangential_load(85, 3.2, 4000)

#sigma()