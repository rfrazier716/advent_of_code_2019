import common_dependencies.intcode as intcode
import numpy as np
from collections import defaultdict
from pathlib import Path
from random import choice
import json  # used to save the navigation data
import re  # used to reparse the json data

map_visualization = {
    0: "#",
    1: ".",
    2: "@"
}

# dictionary of directions, the input to the computer, and the position modifier associated with them
direction = {
    "N": (1, (0, 1)),
    "S": (2, (0, -1)),
    "W": (3, (-1, 0)),
    "E": (4, (1, 0))
}

reverse_direction = {
    "N": "S",
    "S": "N",
    "W": "E",
    "E": "W"
}


def get_adjacent_coordinates(coord):
    # returns a set of adjacent coordinates
    return set([add_tuple(coord, value[1]) for _, value in direction.items()])


def get_adjacent_spaces(coord, open_spaces):
    adjacent_spaces = get_adjacent_coordinates(coord).intersection(open_spaces)
    return adjacent_spaces


def subtract_tuple(coord_1, coord_2):
    # subtracts two coordinates of N-Dimensions and returns a tuple as the result
    return tuple([a - b for a, b in zip(coord_1, coord_2)])


def add_tuple(coord_1, coord_2):
    # adds two coordinates of N-Dimensions and returns a tuple as the result
    return tuple([a + b for a, b in zip(coord_1, coord_2)])


def build_graph(map_dict):
    spaces = set([key for key, item in map_dict.items() if item != 0])  # the set of open, explored spaces in the map
    graph = {key: get_adjacent_spaces(key, spaces) for key, item in map_dict.items() if item != 0}
    return graph  # return the graph object

    # want to build a graph of vectors which have coordinates and all adjacent values that are not walls


class RepairDroid(intcode.IntcodeComputer):
    _map_bounds = 50  # how far to span the map

    def __init__(self, memory=np.array(()), verbose=False):
        self._c_verbose = verbose  # if the child is verbose
        self._position = (0, 0)  # the droids position, must be a tuple
        super().__init__(memory, verbose=False)  # initialize the computer core
        self.reset()

    def reset(self):
        self._canister_position = None
        self._history = []  # history is a list of all the choices sent to the droid
        self._map = defaultdict(int)  # initialize the droids map which records all explored areas
        self._map[(0, 0)] = 1  # the value of the map at the origin must be 0 because the robot is there
        self._v_map = [[" "] * (2 * self._map_bounds + 1) for _ in
                       range(2 * self._map_bounds + 1)]  # initialize the visual map
        # 1-> space
        # 0 -> wall
        # 2 -> O2 System
        super().reset()  # call the intcode computer's reset function as well

    def move(self, move_direction):
        input = direction[move_direction][0]
        self.input(input)  # input the direction to move
        self.resume()  # run the software
        droid_response = int(self.flush_output()[0])  # need to typecast to int
        new_position = add_tuple(self._position, direction[move_direction][1])
        self._map[new_position] = droid_response  # update the map with what is in that location
        self._update_visual_map(new_position, map_visualization[droid_response])
        if droid_response != 0:
            self._position = new_position  # update the position if we didn't hit a wall
            self._history.append(move_direction)  # update the position onto the move direction stack
        if self._c_verbose:
            print("Attempting to move {}({}) received response {}. new position={}".format(move_direction, input,
                                                                                           droid_response,
                                                                                           self._position))

    def backtrack(self):
        # back track the droid to a previous cell, don't need to update map or process response
        backtrack_direction = reverse_direction[self._history.pop(-1)]  # pop a value off the stack
        input = direction[backtrack_direction][0]
        self.input(input)  # input the direction to move
        self.resume()  # run the software
        new_position = add_tuple(self._position, direction[backtrack_direction][1])
        self._position = new_position  # update the droids position
        response = self.flush_output()[0]
        if response == 0:
            # if we didn't backtrack into open space raise an error
            raise ValueError("Droid Backtracked into a wall")
        if self._c_verbose:
            print("No valid options to explore, backtracking {}".format(backtrack_direction))

    def _update_visual_map(self, position, value):
        self._v_map[self._map_bounds - position[1]][self._map_bounds + position[0]] = value

    def find_unexplored_adjacencies(self):
        # returns a list of directions that the droid has yet to explore
        adjacent_coordinates = get_adjacent_coordinates(self._position)  # get the set of nearby coordinates
        # unexplored coordinates is the difference in the set of adjacent coords from the set of explored coords
        unexplored_coordinates = adjacent_coordinates.difference(set(self._map.keys()))
        # convert the position tuples back to cardinal direction commands for the bot
        unexplored_directions = [
            {(0, 1): "N", (0, -1): "S", (-1, 0): "W", (1, 0): "E"}[subtract_tuple(coord, self._position)]
            for coord in unexplored_coordinates]
        return unexplored_directions

    def explore(self):
        # explore the map and return when the droid has found the O2 canister
        while True:  # loop until we throw an error trying to backtrack
            if self._map[self._position] == 2:  # if we found the canister record it
                self._canister_position = self._position
            unexplored_directions = self.find_unexplored_adjacencies()
            if self._c_verbose: print("potential spaces to explore {}".format(unexplored_directions))
            if unexplored_directions:  # if the list is not empty pick an option and advance to the next step
                movement_dir = choice(unexplored_directions)
                self.move(movement_dir)  # move in that direction
            else:  # if we can't go any more, pop off the stack and repeat
                try:
                    self.backtrack()
                except IndexError:
                    break
                    # if we try to backtrack and the history stack is empty we've explored the entire map and
                    # returned to the start

    def draw_map(self):

        self._update_visual_map((0, 0), "*")  # put an asterik at the origin
        self._update_visual_map(self._position, "R")  # put a marker where the robot is
        print("\n".join(["".join(row) for row in self._v_map]))  # print the map as a 2D grid
        self._update_visual_map(self._position, ".")  # delete the robot marker for future calls

    @property
    def position(self):
        return self._position

    @property
    def map(self):
        # return the map dictionary
        return self._map

    @property
    def canister_position(self):
        return self._canister_position


def generate_map():
    # generate the map and put it into a json file
    puzzle_input_path = Path("puzzle_inputs") / "day15_input.txt"
    int_code = np.loadtxt(puzzle_input_path, delimiter=",")
    droid = RepairDroid(int_code, verbose=False)
    droid.explore()
    droid.draw_map()
    map_data = {}
    map_data["canister"] = droid.canister_position
    map_data["map"] = {str(key): value for key, value in
                       droid.map.items()}  # need to convert keys to string so JSON can process
    with open("Day15_map.json", "w+") as file:
        # save the data to a json file to speed up future tests
        json.dump(map_data, file)
    return droid.map


def string_to_tuple(string):
    return tuple([int(num) for num in re.findall("-*[0-9]+", string)])


def get_map_data():
    map_loaded = False
    while not map_loaded:
        try:
            # try to open the map data, if it doesn't exist, generate it
            with open("Day15_map.json", 'r') as file:
                map_data = json.load(file)
                canister_position = tuple(map_data["canister"])  # load the canister position back
                map_dict={string_to_tuple(key): value for key,value in map_data["map"].items()} # load map dict
                map_loaded = True  # set flag that the map has correctly loaded
        except FileNotFoundError:
            # if no map data exists, create it
            print("map data not found, generating map from droid")
            generate_map()  # generate the map data using a droid
    return canister_position, map_dict


def breadth_first_search(graph, origin=(0, 0), target=(0, 0)):
    # breadth first search that finds the shortest distance between two points
    visited = defaultdict(bool)  # dictionary that keeps track of which nodes we've visited
    bfs_queue = [(0, origin)]  # queue that holds the position and number of steps for bfs
    dist, vertex = bfs_queue.pop()  # pop item off queue
    max_depth=0
    while vertex != target:
        for adjacent in graph[vertex]:
            if not visited[adjacent]:  # if we haven't visited this vertex yet
                visited[adjacent] = True  # update visited dict
                bfs_queue.append((dist + 1, adjacent))
        try:
            dist, vertex = bfs_queue.pop(0)  # pop next item off queue
            if dist>max_depth:
                max_depth=dist  #if we've descended further than before update the queue
        except IndexError:
            # if there's an index error exit the loop and return the furthest depth we've descended
            print("tried to pull from empty queue")
            return max_depth
        # print("{1} is {0} steps away".format(dist, vertex))
    return dist

def puzzle_part_a(graph,target):
    distance_to_canister=breadth_first_search(graph, target=target)
    print("Droid is {} steps away from canister on shortest path".format(distance_to_canister))

def puzzle_part_b(graph,canister_position):
    # want to know how long to fill the entire space with O2
    # assign BFS an impossible location to reach, and the origin as the O2 canister
    max_distance=breadth_first_search(graph,origin=canister_position,target=(100,100))
    print("the maximum depth of this search before exhaustion is {}".format(max_distance))

def main():
    print("Importing Map from file")
    canister_position, map_dict = get_map_data()  # either import the map data or have the droid navigate it
    graph = build_graph(map_dict)  # a dictionary of coordinates and adjacent white spaces
    print("\n**puzzle part A**")
    puzzle_part_a(graph,canister_position)
    print("\n**puzzle part B**")
    puzzle_part_b(graph,canister_position)

if __name__ == "__main__":
    main()
