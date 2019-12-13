import numpy as np
from pathlib import Path
import common_dependencies.intcode as intcode

def parse_int_code(int_code):
	computer=intcode.IntcodeComputer()
	computer.load_memory(np.array([1,1,1,4,99,5,6,0,99]))
	mem_result=computer.run()
	print(mem_result)

def main():
	puzzle_input_path=Path("puzzle_inputs") / "day13_input.txt"
	int_code=np.loadtxt(puzzle_input_path, delimiter=",")
	parse_int_code(int_code)

if __name__=="__main__":
	main()