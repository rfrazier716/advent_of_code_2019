import numpy as np

np.seterr(divide='ignore')  # don't do anything if you divide by zero

from pathlib import Path
import itertools

class Asteroid():
    def __init__(self,position):
        self._position=position
        self.visible_asteroid_directions=[]
    @property
    def position(self):
        return self._position

    @property
    def total_visible_asteroids(self):
        return len(np.unique(self.visible_asteroid_directions))

def colinear_points(points):
    np_pts = np.array(points).T  # turn into a numpy object

    print(np.divide(1, 0))
    slope_arr = np.divide(
        *np.diff(np_pts))  # slope is the difference between x coords divided by the difference between y coords
    return np.all(slope_arr == slope_arr[0])


def angle(pt_a, pt_b):
    rise=pt_b[1] - pt_a[1]
    run=pt_b[0] - pt_a[0]

    angle_between_points=np.arctan2(run,rise)
    try:
        return angle_between_points[0]
    except IndexError:
        return angle_between_points

def distance(pt_a,pt_b):
    rise = pt_b[1] - pt_a[1]
    run = pt_b[0] - pt_a[0]
    return np.sqrt(rise**2+run**2)



def asteroids_from_file(puzzle_input_file):
    asteroids = []
    with open(puzzle_input_file) as file:
        row = 0  # row which translates to what lines being read
        for y, line in enumerate(file.readlines()):
            for x, letter in enumerate(line):
                if letter == "#":
                    asteroids.append(Asteroid((x, y)))
    return asteroids

def sorted_list_bin_indices(list):
    #takes a sorted list and returns a list of values where l[n]!=l[n-1]
    current_value=list[0]
    bin_indices=[0]
    for j,item in enumerate(list):
        if item!=current_value:
            bin_indices.append(j)
            current_value=item
    return bin_indices

def puzzle_part_a(asteroids):
    for asteroid_a,asteroid_b in itertools.combinations(asteroids,2):
        asteroid_angle=angle(asteroid_a.position,asteroid_b.position)
        asteroid_a.visible_asteroid_directions.append(angle(asteroid_a.position,asteroid_b.position))
        asteroid_b.visible_asteroid_directions.append((asteroid_angle+np.pi) % (2*np.pi))
    print(asteroids[np.argmax([asteroid.total_visible_asteroids for asteroid in asteroids])].position)
    print(np.max([asteroid.total_visible_asteroids for asteroid in asteroids]))

def puzzle_part_b(asteroids):
    moon_base_coord=(17,23)
    angle_arr,distance_arr,position_arr=np.array([(-angle(moon_base_coord,asteroid.position)+np.pi/2, distance(moon_base_coord,asteroid.position),asteroid.position) for asteroid in asteroids]).T
    sort_indices=np.lexsort((distance_arr,angle_arr))
    angle_arr,distance_arr,position_arr=[arr[sort_indices] for arr in (angle_arr,distance_arr,position_arr)]  #sort the arrays in ascending order of angle

    bin_indices=sorted_list_bin_indices(angle_arr)
    binned_positions=[position_arr[bin_indices[j-1]:bin_indices[j]] for j in range(1,len(bin_indices))]
    print([position[0] for position in binned_positions][199])

def main():
    puzzle_input_file = Path("puzzle_inputs") / "day10_input.txt"
    asteroids = asteroids_from_file(puzzle_input_file)
    puzzle_part_a(asteroids)
    puzzle_part_b(asteroids)



if __name__ == "__main__":
    main()
