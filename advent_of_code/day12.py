import numpy as np
import itertools
from pathlib import Path
import re
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def energy(vector):
    return np.sum(np.abs(vector))


def apply_acceleration(body_a, body_b):
    # Difference of the two position vectors give a vector from A pointing to B
    distance = np.subtract(body_b.position, body_a.position)
    distance_sign = np.sign(distance)  # sign of the distance
    body_a.velocity =np.add(body_a.velocity,distance_sign)
    body_b.velocity =np.subtract(body_b.velocity,distance_sign)


def print_satellite_info(satellite):
    coord_string = "<x= {}, y= {}, z= {}>"
    pos_string = "pos=" + coord_string.format(*satellite.position)
    vel_string = "vel=" + coord_string.format(*satellite.velocity)
    kin_string = "kin: {}".format(satellite.kinetic_u)
    pot_string = "pot: {}".format(satellite.potential_u)
    tot_string = "tot: {}".format(satellite.total_u)
    print(pos_string + "\t" + vel_string + "\t" + kin_string + "\t" + pot_string + "\t" + tot_string)


class Satellite(object):
    def __init__(self, position=np.array([0, 0, 0]), velocity=np.array([0, 0, 0]), name=""):
        self.name = name
        self._position = position
        self._velocity = velocity

    def apply_velocity(self):
        self._position = np.add(self._position, self._velocity)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        self._velocity = velocity

    @property
    def potential_u(self):
        return energy(self._position)

    @property
    def kinetic_u(self):
        return energy(self._velocity)

    @property
    def total_u(self):
        return energy(self._position) * energy(self._velocity)


class MultiBodySystem(object):
    def __init__(self, bodies):
        self._bodies = bodies

    @property
    def bodies(self):
        return self._bodies

    def get_system_state(self):
        for body in self._bodies:
            print_satellite_info(body)

    def advance_state(self):
        # for every body, check what pull the other bodies have on it to update velocity
        for body_a, body_b in itertools.combinations(self._bodies, 2):
            apply_acceleration(body_a, body_b)
        # update position of each planet based on velocity
        for body in self._bodies:
            body.apply_velocity()

    @property
    def system_energy(self):
        return np.sum([satellite.total_u for satellite in self._bodies])

def parse_puzzle_input(path):
    # takes the puzzle path and returns a 4x3 numpy array with initial coordinates
    with open(path) as file:
        coords = np.full((4, 3), 0)
        for line_num, line in enumerate(file.readlines()):
            coords[line_num, :] = np.array([int(j) for j in re.findall(r'-?[0-9]+', line)])
    return coords

def puzzle_part_a(bodies):
    system = MultiBodySystem(bodies)
    [system.advance_state() for _ in range(1000)] #advance the system 10 steps
    print("after 200 steps:")
    system.get_system_state()
    print("total system energy: {}".format(system.system_energy))

def bodies_in_same_state(body_a,body_b):
    #check if two planets have identical position and velocity
    matched=False
    if np.array_equal(body_a.position,body_b.position):
        if np.array_equal(body_a.velocity,body_b.velocity):
            matched=True
    return matched

def puzzle_part_b(bodies,verbose=False):
    #make a new system
    # need to figure out how many steps for the independent coordinate of a planet to return to it's original state
    # the time for the planet to return to it's initial state is the product of the independent coordinates

    #run simulation
    #check if any position coordinate matches it's initial position coordinate
    #if so write that value into the periodicity matrix
    initial_position_matrix =np.array([body.position for body in bodies])
    initial_position_vector=np.sum(initial_position_matrix,0)
    periodicity_vector=np.full(3,0,dtype='uint64') #matrix that tracks the periodicity values for each coordinate
    system=MultiBodySystem(bodies) #make our system
    step=0 #step counter
    while np.isin(periodicity_vector,0).any():   #loop until the periodicity matrix is entirely filled
        step+=1    #increment the step counter
        system.advance_state()  # step the system
        current_position_matrix=np.array([body.position for body in system.bodies])
        current_velocity_matrix=np.array([body.velocity for body in system.bodies])
        current_position_vector=np.sum(current_position_matrix,0)
        current_velocity_vector=np.sum(current_velocity_matrix,0)
        position_difference=np.subtract(current_position_vector,initial_position_vector)
        for zeroed_index in range(3):
            # check how the positions have changed from the initial state
            if np.array_equal(current_position_matrix[:,zeroed_index],initial_position_matrix[:,zeroed_index]) and np.array_equal(current_velocity_matrix[:,zeroed_index],np.full(4,0)):
                if verbose: print("Coordinate Axis {} has returned to initial state after {} steps".format(zeroed_index,step))
                if periodicity_vector[zeroed_index]==0:  #if we don't already have a value for the periodicity set it
                    if verbose: print("Updating Periodicity Matrix")
                    periodicity_vector[zeroed_index]=step
                else:
                    if verbose: print("Periodicity Matrix already has value of {}, will not overwrite with {}".format(periodicity_vector[zeroed_index],step))
    [print("Axis {} oscillates with a period of {}".format(j,period)) for j,period in enumerate(periodicity_vector)]
    print("Total Steps before system resets {}".format(np.lcm.reduce(periodicity_vector)))

def tracking_planet(bodies):
    # make a new system
    system = MultiBodySystem(bodies)
    n_runs=100
    plotted=np.full((n_runs,len(bodies),3),0)
    for j in range(n_runs):
        #system.get_system_state()
        plotted[j]=np.array([body.position for body in system.bodies])
        system.advance_state()
    fig = plt.figure()
    subplots=[221,222,223,224]
    planet_positions=[plotted[:,j,:] for j in range(len(bodies))]
    for j,planet_position in enumerate(planet_positions):
        plt.subplot(subplots[j])
        for coord in planet_position.T:
            plt.plot(coord,marker=".")
    plt.show()


def main():
    puzzle_input_file = Path("puzzle_inputs") / "day12_input.txt"
    moon_coordinates=parse_puzzle_input(puzzle_input_file) # get puzzle input and return as a numpy array
    bodies = [Satellite(coord) for coord in moon_coordinates]  # construct bodies for system
    puzzle_part_a(copy.deepcopy(bodies))
    puzzle_part_b(copy.deepcopy(bodies),verbose=False)
    #tracking_planet(copy.deepcopy(bodies))



if __name__ == "__main__":
    main()
