import numpy as np
from pathlib import Path
import common_dependencies.intcode as intcode
from enum import Enum

class Vector():
    # basic vector class
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __abs__(self):
        return np.sqrt(self.x ** 2 + self.y ** 2)

    def __str__(self):
        return "<{},{}>".format(self.x, self.y)

    @property
    def arr(self):
        return np.array((self.x, self.y))


class Tile():
    display_dict = {
        0: " ",
        1: "#",
        2: "B",
        3: "=",
        4: "O"
    }

    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

    @property
    def ascii(self):
        return self.display_dict[self.type]


class ArcadeCabinet(intcode.IntcodeComputer):
    # arcade cabinet is a child of Intcode computer but has a screen
    def __init__(self, memory=np.array(()), verbose=False):
        self._verbose = verbose
        self._h_lines = 0  # horizontal scan size of the display
        self._v_lines = 0  # Vertical scan size
        self._score = 0  # score of the user
        self._screen_buffer = []
        self._screen = None

        self._ball_position = Vector(0, 0)  # position of the ball
        self._ball_velocity = Vector(0, 0)  # velocity of the ball
        self._paddle_position = Vector(0, 0)  # where the paddle is
        super().__init__(memory,verbose)  # initialize the computer core

    def update(self):
        self.resume()  # advance the computer until it's done running
        self._screen_buffer = []
        for packet in np.array(self.flush_output()).reshape((-1, 3)):  # load the screen buffer with the computer output
            if packet[0] == -1:  # if we got the score output
                self._score = packet[2]
            else:
                if packet[2] == 4:  # if this is the ball coordinate
                    self._ball_velocity = Vector(*packet[:2]) - self._ball_position  # update the ball velocity
                    self._ball_position = Vector(*packet[:2])  # update the ball position
                elif packet[2] == 3:  # if this is the paddle
                    self._paddle_position = Vector(*packet[:2])
                self._screen_buffer.append(Tile(*packet))
        #update the screen
        self.update_screen()
        if self._verbose:
            self.print_summary()

    def update_screen(self):
        if self._h_lines == 0 or self._v_lines == 0:
            # If we don't know the dimensions of the screen yet, draw it
            self._h_lines = np.max([tile.x for tile in self._screen_buffer]) + 1
            self._v_lines = np.max([tile.y for tile in self._screen_buffer]) + 1
            self._screen=np.full((self._v_lines,self._h_lines)," ")   # initialize the screen
        for tile in self._screen_buffer:
            self._screen[tile.y,tile.x]=tile.ascii

    def draw_screen(self):
        display=""
        for row in self._screen:
            display += "".join([character for character in row]) + '\n'
        print("Score: {}".format(self._score))
        print(display)

    def print_summary(self):
        print("Score {}".format(self._score))
        print("Ball Position {}".format(self._ball_position))
        print("Ball Velocity {}".format(self._ball_velocity))
        print("Paddle Position {}".format(self._paddle_position))

    @property
    def score(self):
        return self._score

    @property
    def screen_buffer(self):
        return self._screen_buffer

    @property
    def ball_position(self):
        return self._ball_position

    @property
    def ball_velocity(self):
        return self._ball_velocity

    @property
    def paddle_position(self):
        return self._paddle_position


def puzzle_part_a(cabinet):
    cabinet.reset()  # reset the computer
    cabinet.update()  # resume operation
    n_blocks = np.count_nonzero(np.array([tile.type for tile in cabinet.screen_buffer]) == 2)
    print("There are {} blocks in the screen buffer".format(n_blocks))


def puzzle_part_b(cabinet):
    print("Running Part B")
    cabinet.reset()  # reset the computer
    total_steps=0
    while not cabinet.program_finished:
        cabinet.update()
        total_steps+=1
        paddle_distance=(cabinet.ball_position-cabinet.paddle_position).x
        ball_direction=cabinet.ball_velocity.x
        joystick_input=0
        if paddle_distance!=0 and ball_direction!=0:  #if we are not directly under the paddle and the ball is moving, move towards it
            joystick_input=np.sign(paddle_distance)
        else:
            #if we're under the ball move in the same direction as it
            joystick_input=ball_direction
        cabinet.input(joystick_input)  # don't do anything with the joystick
        #cabinet.print_summary()
        #cabinet.draw_screen()
    print(total_steps)
    cabinet.draw_screen()


def main():
    puzzle_input_path = Path("puzzle_inputs") / "day13_input.txt"
    int_code = np.loadtxt(puzzle_input_path, delimiter=",")
    int_code[0] = 2  # put in two quarters to play the game
    cabinet = ArcadeCabinet(int_code, verbose=False)
    puzzle_part_a(cabinet)
    puzzle_part_b(cabinet)


if __name__ == "__main__":
    main()
