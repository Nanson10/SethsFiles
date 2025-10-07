import math
#Calibration#

#Car stats#
pi = math.pi
wheel_weight_kilograms = 4.67
motor_weight_kilograms = 10.4 # Don't know where this goes.
wheel_diameter_meters = .5588
total_car_weight_kilograms = 260
motor_diameter_meters = .262 # Don't know where this goes.
wheel_inertia = 0.5 * wheel_weight_kilograms * (wheel_diameter_meters / 2) ** 2

#Data parameters#
max_meters_per_second = 44 # Runs energy simulation up to {} mps
change_in_meters_per_second = 0.01 # The change in mps between iterations

#------ Inverse Energy Function ------#
#Fuck the real math

#Unfucked the real math :)
def main():
    wheels_rotational_energy = []
    total_kinetic_energy = []

    iterations = int(max_meters_per_second / change_in_meters_per_second)
    for i in range(0, iterations, 1):
        current_meters_per_second = i * change_in_meters_per_second
        # How fast the wheels need to spin to match car speed
        revolutions_per_second_of_wheels = current_meters_per_second / (pi * wheel_diameter_meters) # rev per second = speed / circumference
        radians_per_second_of_wheels = revolutions_per_second_of_wheels * 2 * pi # There are 2 pi radians per revolution

        # Calculate rotational energy of the wheels
        rotational_energy_of_a_wheel = 0.5 * wheel_inertia * radians_per_second_of_wheels ** 2
        rotational_energy_of_wheels = rotational_energy_of_a_wheel * 3 # Because we use 3 wheels

        # Calculate the translational energy of the car
        translational_energy_of_car = 0.5 * total_car_weight_kilograms * current_meters_per_second ** 2

        # Total kinetic energy is the sum of kinetic (translational) energy of the car moving and the rotational energy of the wheels.
        total_energy_of_car = translational_energy_of_car + rotational_energy_of_wheels
        
        wheels_rotational_energy.append(rotational_energy_of_wheels)
        total_kinetic_energy.append(total_energy_of_car)

    sourcefile = open(r"./rotational_energy.txt", 'w')
    for index in range(0, iterations, 1):
        print(wheels_rotational_energy[index], file = sourcefile)
    sourcefile.close()

    sourcefile = open(r"./kinetic_energy.txt", 'w')
    for index in range(0, iterations, 1):
        print(total_kinetic_energy[index], file = sourcefile)
    sourcefile.close()
    print("Energies computed")

main()