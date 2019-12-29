import common_dependencies.intcode as intcode
import numpy as np
from collections import defaultdict
from pathlib import Path
from random import choice


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


def get_adjacent_coordinate(coord):
    # returns a set of adjacent coordinates
    return set([add_tuple(coord, value[1]) for _, value in direction.items()])


def subtract_tuple(coord_1, coord_2):
    # subtracts two coordinates of N-Dimensions and returns a tuple as the result
    return tuple([a - b for a, b in zip(coord_1, coord_2)])


def add_tuple(coord_1, coord_2):
    # adds two coordinates of N-Dimensions and returns a tuple as the result
    return tuple([a + b for a, b in zip(coord_1, coord_2)])


class RepairDroid(intcode.IntcodeComputer):
    _map_bounds = 50  # how far to span the map
    def __init__(self, memory=np.array(()), verbose=False):
        self._c_verbose = verbose  # if the child is verbose
        self._position = (0, 0)  # the droids position, must be a tuple
        super().__init__(memory, verbose=False)  # initialize the computer core
        self.reset()

    def reset(self):
        self._canister_position=None
        self._history = []  # history is a list of all the choices sent to the droid
        self._map = defaultdict(int)  # initialize the droids map which records all explored areas
        self._map[(0, 0)] = 1  # the value of the map at the origin must be 0 because the robot is there
        self._v_map=[[" "]*(2*self._map_bounds+1) for _ in range(2*self._map_bounds+1)] # initialize the visual map
        # 1-> space
        # 0 -> wall
        # 2 -> O2 System
        super().reset()  # call the intcode computer's reset function as well

    def move(self, move_direction):
        input = direction[move_direction][0]
        self.input(input)  # input the direction to move
        self.resume()  # run the software
        droid_response = self.flush_output()[0]
        new_position = add_tuple(self._position, direction[move_direction][1])
        self._map[new_position] = droid_response  # update the map with what is in that location
        self._update_visual_map(new_position,map_visualization[droid_response])
        if droid_response != 0:
            self._position = new_position  # update the position if we didn't hit a wall
            self._history.append(move_direction)  # update the position onto the move direction stack
        if self._c_verbose:
            print("Attempting to move {}({}) received response {}. new position={}".format(move_direction, input,
                                                                                           droid_response,
                                                                                           self._position))
    def backtrack(self):
        #back track the droid to a previous cell, don't need to update map or process response
        backtrack_direction = reverse_direction[self._history.pop(-1)]  # pop a value off the stack
        input = direction[backtrack_direction][0]
        self.input(input)  # input the direction to move
        self.resume()  # run the software
        new_position = add_tuple(self._position, direction[backtrack_direction][1])
        self._position=new_position #update the droids position
        response=self.flush_output()[0]
        if response==0:
            #if we didn't backtrack into open space raise an error
            raise ValueError("Droid Backtracked into a wall")
        if self._c_verbose:
            print("No valid options to explore, backtracking {}".format(backtrack_direction))

    def _update_visual_map(self, position, value):
        self._v_map[self._map_bounds - position[1]][self._map_bounds + position[0]] = value

    def find_unexplored_adjacencies(self):
        # returns a list of directions that the droid has yet to explore
        adjacent_coordinates = get_adjacent_coordinate(self._position)  # get the set of nearby coordinates
        # unexplored coordinates is the difference in the set of adjacent coords from the set of explored coords
        unexplored_coordinates = adjacent_coordinates.difference(set(self._map.keys()))
        # convert the position tuples back to cardinal direction commands for the bot
        unexplored_directions = [
            {(0, 1): "N", (0, -1): "S", (-1, 0): "W", (1, 0): "E"}[subtract_tuple(coord, self._position)]
            for coord in unexplored_coordinates]
        return unexplored_directions


    def explore(self):
        # explore the map and return when the droid has found the O2 canister
        while self._map[self._position]!=2: #loop as long as we have not found the O2 canister
            unexplored_directions=self.find_unexplored_adjacencies()
            if self._c_verbose: print("potential spaces to explore {}".format(unexplored_directions))
            if unexplored_directions:   #if the list is not empty pick an option and advance to the next step
                movement_dir=choice(unexplored_directions)
                self.move(movement_dir) #move in that direction
            else:   # if we can't go any more, pop off the stack and repeat
                self.backtrack()

    def draw_map(self):

        self._update_visual_map((0, 0), "*")    #put an asterik at the origin
        self._update_visual_map(self._position,"R") # put a marker where the robot is
        print("\n".join(["".join(row) for row in self._v_map]))   #print the map as a 2D grid
        self._update_visual_map(self._position,".")# delete the robot marker for future calls


    @property
    def position(self):
        return self._position


def main():
    puzzle_input_path = Path("puzzle_inputs") / "day15_input.txt"
    int_code = np.loadtxt(puzzle_input_path, delimiter=",")
    droid = RepairDroid(int_code, verbose=True)
    droid.explore()
    droid.draw_map()



if __name__ == "__main__":
    main()
