#Calibration#

pi = 3.1415
wheel_weight = 4.67
motor_weight = 10.4
wheel_dia = .5588

weight = 260

motor_dia = .262
#------ Inverse Energy Function ------#
#Fuck the real math
def main():
    rotational_energy = []
    std_kinetic_energy = []

    #Range of 4400 = 44m/s, gives accuracy up to 100mph with percision of .01 m/s
    for i in range(0, 4400, 1):
        i /= 100
        rpm_required = i / (2 * pi * (wheel_dia / 2))
        rotational_energy.append(0.5 * ((3 * wheel_weight * (wheel_dia / 2)**2) + (motor_weight * (motor_dia / 2)**2)) * rpm_required ** 2)
        std_kinetic_energy.append(0.5 * weight * i ** 2)

    sourcefile = open(r"C:\Users\schae\Documents\Purdue_Solar_Racing\Calculation_Tool\rotational_energy.txt", 'w')
    for i in range(0, 4400, 1):
        print(rotational_energy[i], file = sourcefile)
    sourcefile.close()

    sourcefile = open(r"C:\Users\schae\Documents\Purdue_Solar_Racing\Calculation_Tool\kinetic_energy.txt", 'w')
    for i in range(0, 4400, 1):
        print(std_kinetic_energy[i], file = sourcefile)
    sourcefile.close()
    print("HI")

main()