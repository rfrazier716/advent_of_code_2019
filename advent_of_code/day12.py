import numpy as np
import itertools


def energy(vector):
    return np.sum(np.abs(vector))


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
        self.name=name
        self._position = position
        self._velocity = velocity

    def apply_velocity(self):
        self._position=np.add(self._position,self._velocity)

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
        self._position = velocity
        self._potential_u = energy(velocity)

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
    def __init__(self,bodies):
        self._bodies=bodies

    def get_system_state(self):
        for body in self._bodies:
            print_satellite_info(body)

    def advance_state(self):
        pass
        #for every body, check what pull the other bodies have on it to update velocity
        for bodyA,bodyB in itertools.combinations(self._bodies,2): #Will generate a list of bodies to compare without repeats
            distance=np.subtract(bodyB.position,bodyA.position) #Difference of the two position vectors give a vector from A pointing to B
            distance_sign=np.sign(distance)
            print(distance)
        #update position of each planet based on velocity
def main():
    bodies=[Satellite(name=str(j)) for j in range(4)]
    system=MultiBodySystem(bodies)
    system.advance_state()



if __name__ == "__main__":
    main()
