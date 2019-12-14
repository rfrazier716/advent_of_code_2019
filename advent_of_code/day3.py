import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
import itertools

def find_intersection_points(wires):
    intersections=[]
    total_steps=[]
    steps_a=0
    for segment_a in wires[0]:
        steps_b = 0
        for segment_b in wires[1]:
            if not parallel_lines(segment_a,segment_b):
                intersection=orthogonal_intersection(segment_a,segment_b)
                if intersection is not None and intersection!=(0,0):
                    #update the total number of steps the wire has taken to get here:
                    steps_to_intersection_a=steps_a+abs(np.sum(intersection-segment_a.start)) #how many integer steps it took to get here
                    steps_to_intersection_b=steps_b+abs(np.sum(intersection-segment_b.start))
                    #print("Intersection:")
                    #print("\t"+segment_a.descriptor)
                    #print("\t"+segment_b.descriptor)
                    print("\tintersect at Coordinate ({},{})\n".format(*intersection))
                    print("\twire A has taken {} steps".format(steps_to_intersection_a))
                    print("\twire B has taken {} steps".format(steps_to_intersection_b))
                    intersections.append(intersection)
                    total_steps.append(steps_to_intersection_a+steps_to_intersection_b)
            steps_b+=segment_b.length
        steps_a += segment_a.length
        print("{}\t{}".format(steps_a,steps_b))
    return intersections,total_steps

def display_wires(wires,intersections=[]):
    for wire in wires:
        plt.plot(*(np.array([(0,0)]+[line.end for line in wire]).T))
    plt.scatter(*(np.array(intersections).T))
    plt.show()

def orthogonal_intersection(line_1, line_2):
    # checks if two line segments intersect and returns the tuple of intersection, if they do not intersect returns None
    # Only works for lines orthogonal line in the X and Y direction
    # check if line 1 is horizontal or vertical
    if line_1.unit_vector[0] == 1:  # if the line is horizontal
        t_val = (line_2.start - line_1.start)[0] / (
                    line_1.length * line_1.unit_vector.sum())  # the variable for the vector equation of line 1 where it intercepts line 2
        u_val = (line_1.start - line_2.start)[1] / (
                    line_2.length * line_2.unit_vector.sum())  # same but for line 2 X line 1
        if u_val >= 0 and u_val <= 1 and t_val >= 0 and t_val <= 1:
            # if the u_val and the t_val are within 0 to 1 the intersection point is on the line segment
            return (line_2.start[0],line_1.start[1])
    else:  # otherwise the line is vertical
        t_val = (line_2.start - line_1.start)[1] / (line_1.length * line_1.unit_vector.sum())
        u_val = (line_1.start - line_2.start)[0] / (line_2.length * line_2.unit_vector.sum())
        if u_val >= 0 and u_val <= 1 and t_val >= 0 and t_val <= 1:
            # if the u_val and the t_val are within 0 to 1 the intersection point is on the line segment
            return (line_1.start[0],line_2.start[1])
    return None  # if the lines do not intercept return a none type


def parallel_lines(line_1, line_2):
    return np.array_equal(*[line.abs_unit_vector for line in [line_1, line_2]])


def generate_lines_from_offsets(offset_array):
    starting_point = np.array((0, 0))  # prime the loop so that the first line segment in the wire starts at the origin
    line_segments = []
    for transform in offset_array:
        direction = transform[0]  # direction is the first character of the transform instruction
        distance = int(transform[1:])  # distance is the remaining data
        #print("Generating line at point ({},{})".format(*starting_point) + " with length {} heading ".format(distance) + direction)
        line_segments.append(OrthoLineSeg(starting_point,distance,direction.lower()))
        starting_point=line_segments[-1].end  # make the new starting point the end point of the previous line
    return line_segments


class OrthoLineSeg(object):
    # an orthogonal line segment that can be either vertical or horizontal
    _unit_vector_dict = dict(u=(0, 1), d=(0, -1), l=(-1, 0), r=(1, 0))

    def __init__(self, origin=(0, 0), length=1, direction="r"):
        self._origin = origin
        self._length = length
        self._unit_vector = np.array(self._unit_vector_dict.get(direction.lower()))
        self._pts = (np.array(origin), np.array(origin + length * self._unit_vector))

    @property
    def descriptor(self):
        return "({},{})->".format(*self._pts[0])+"({},{})".format(*self._pts[1])

    @property
    def length(self):
        return self._length

    @property
    def start(self):
        return self._pts[0]

    @property
    def end(self):
        return self._pts[1]

    @property
    def unit_vector(self):
        return self._unit_vector

    @property
    def abs_unit_vector(self):
        return np.abs(self.unit_vector)


def main():
    puzzle_input_path= Path("puzzle_inputs") / "day3_input.txt"
    wires=[] # list that holds the wires
    print("importing wire coordinates from file")
    with open(puzzle_input_path) as file:
        for line in file.readlines():
            wires.append(generate_lines_from_offsets(line.split(',')))
    print("calculating intersection points")
    intersection_points,steps_at_intersection=find_intersection_points(wires) #find the intersection points of the two wires

    manhattan_distance=np.apply_along_axis(np.sum,1,np.abs(intersection_points))
    print("minimum distance of Intersection to origin is: {}".format(np.min(manhattan_distance)))

    #finding the manhattan distance of the intersection with the shortest path
    print(steps_at_intersection)
    shortest_intersection=intersection_points[np.argmin(steps_at_intersection)]
    print("Intersection with fasted travel time is {} with a total path of {}".format(shortest_intersection,np.min(steps_at_intersection)))
    display_wires(wires,intersection_points)

if __name__ == "__main__":
    main()
