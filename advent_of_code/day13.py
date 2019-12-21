import numpy as np
from pathlib import Path
import common_dependencies.intcode as intcode
from enum import Enum

class Tile():
	def __init__(self,x,y,type):
		self.x=x
		self.y=y
		self.type=type

def display_tile(tile):
	display_dict={
		0: "A",
		1: "B",
		2: "C",
		3: "D",
		4: "E"
	}


class ArcadeCabinet(intcode.IntcodeComputer):
	# arcade cabinet is a child of Intcode computer but has a screen
	def __init__(self, memory=np.array(())):
		self._screen_h=38	# horizontal scan size of the display
		self._score=0		# score of the user
		self._screen_buffer=[]
		self._screen=np.full((100,100),0)	#the screen to display the game
		super().__init__(memory)  # initialize the computer core

	def update(self):
		self.resume()	#advance the computer until it's done running
		self._screen_buffer=[]
		for packet in np.array(self.flush_output()).reshape((-1,3)):	#load the screen buffer with the computer output
			if packet[0]==-1:	#if we got the score output
				self._score=packet[2]
			else:
				self._screen_buffer.append(Tile(*packet))

	def draw_screen(self):
		if self._h_lines==0 or self._v_lines==0:
			#If we don't know the dimensions of the screen yet, draw it
			self._h_lines=np.max([tile.x for tile in self._screen_buffer])
			self._v_lines=np.max([tile.x for tile in self._screen_buffer])
		scan_line=''.join([" " for _ in range(self._h_lines)])
		screen=[scan_line for _ in ]

	@property
	def score(self):
		return self._score

	@property
	def screen_buffer(self):
		return self._screen_buffer


def puzzle_part_a(cabinet):
	cabinet.reset()	#reset the computer
	cabinet.update()	#resume operation
	n_blocks=np.count_nonzero(np.array([tile.type for tile in cabinet.screen_buffer])==2)
	print("There are {} blocks in the screen buffer".format(n_blocks))

def puzzle_part_b(cabinet):
	pass

def main():
	puzzle_input_path=Path("puzzle_inputs") / "day13_input.txt"
	int_code=np.loadtxt(puzzle_input_path, delimiter=",")
	int_code[0]=2	#put in two quarters to play the game
	cabinet=ArcadeCabinet(int_code)
	puzzle_part_a(cabinet)


if __name__=="__main__":
	main()