import common_dependencies.intcode as intcode
import numpy as np
from pathlib import Path
import math
from matplotlib import pyplot as plt



class PaintBot(intcode.IntcodeComputer):
    #PaintBot is a child of Intcode computer but has a position value and unit vector for
    _m_rot90=np.array([[0,-1],[1,0]])
    _m_rotn90=np.array([[0,1],[-1,0]])
    def __init__(self,memory=np.array(())):
        self._position=np.array((0,0))  #Paintbot starts at origion
        self._direction=np.array((0,1)) #Paintbot starts by facing up

        super().__init__(memory)  #initialize the computer core

    def move(self):
        self._position=np.add(self._position,self._direction) #move by adding the direction vector to the position

    def turn(self,direction):
        if direction==1:
            #turn right by applying a 90 degree rotation matrix
            self._direction=self._m_rot90.dot(self._direction)
        elif direction==0:
            #turn left by applying a -90 degree rotation matrix
            self._direction=self._m_rotn90.dot(self._direction)

    @property
    def position(self):
        return self._position

    @property
    def direction(self):
        return self._direction
    @property
    def encoded_position(self):
        return 10000*self._position[0]+self._position[1]

def puzzle_part_a(bot):
    paint_history = {}  # empty dictionary object that keeps track of the bots coordinates, the keys are 6 digits where the first 3 are x val and second 3 are y val
    tiles_painted=0
    while not bot.program_finished: #while the programs not finished
        camera_input=0
        try:
            camera_input=paint_history[bot.encoded_position]  #get the color of the current tile, default to white
        except KeyError:
            # if there's a key error this is an unpainted tile and we need to increment the counter
            tiles_painted += 1
        bot.input(camera_input) #provide input to the software
        bot.resume() #resume the software
        new_color,turn_direction=bot.flush_output()
        #print("tile {} was painted {}".format(bot.position,new_color))
        paint_history[bot.encoded_position]=new_color
        bot.turn(turn_direction)
        bot.move()
    print("{} tiles in total were painted".format(tiles_painted))

def decode_coordinate(coordinate):
    x=math.floor(coordinate/10000)
    y=coordinate-10000*x
    return x,y

def puzzle_part_b(bot):
    bot.reset()
    paint_history = {000000:1}  # empty dictionary object that keeps track of the bots coordinates, the keys are 6 digits where the first 3 are x val and second 3 are y val
    tiles_painted = 1
    while not bot.program_finished:  # while the programs not finished
        camera_input = 0
        try:
            camera_input = paint_history[bot.encoded_position]  # get the color of the current tile, default to white
        except KeyError:
            # if there's a key error this is an unpainted tile and we need to increment the counter
            tiles_painted += 1
        bot.input(camera_input)  # provide input to the software
        bot.resume()  # resume the software
        new_color, turn_direction = bot.flush_output()
        # print("tile {} was painted {}".format(bot.position,new_color))
        paint_history[bot.encoded_position] = new_color
        bot.turn(turn_direction)
        bot.move()
    coords=[]
    values=[]
    for coordinate in list(paint_history.keys()):
        coords.append(decode_coordinate(coordinate))
        values.append(paint_history[coordinate])
    white_tiles=(np.argwhere(np.array(values)>0).T)[0]
    print(white_tiles)
    white_coords=np.array([coords[white_tile] for white_tile in white_tiles])
    plt.scatter(white_coords[:,0],white_coords[:,1])
    #plt.xlim((-45,5))
    #plt.ylim((950,1000))
    plt.show()

def main():
    bot=PaintBot()  #initialize teh paint bot
    input_path = Path("puzzle_inputs") / "day11_input.txt"
    program = np.loadtxt(input_path, delimiter=",", dtype=np.int64)
    bot.load_memory(program)
    #puzzle_part_a(bot)
    puzzle_part_b(bot)



if __name__=="__main__":
    main()

