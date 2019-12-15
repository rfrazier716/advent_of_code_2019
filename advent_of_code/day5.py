import numpy as np
from pathlib import Path
import common_dependencies.intcode as intcode

def display_output(computer):
    print("Output:")
    [print(output) for output in computer.flush_output()]

def puzzle_part_a(computer):
    # Part A of the puzzle
    computer.input(1)
    computer.run()
    display_output(computer)

def puzzle_part_b(computer):
    computer.input(5)   #input 5 this time
    computer.run()
    display_output(computer)

def main():
    #load int code from file
    puzzle_input_path=Path("puzzle_inputs") / "day5_input.txt"
    int_code=np.loadtxt(puzzle_input_path, delimiter=",",dtype=int)
    computer=intcode.IntcodeComputer(int_code,verbose=False)

    puzzle_part_a(computer) #run the first part of the puzzle
    computer.load_memory(int_code)  # reload memory
    puzzle_part_b(computer) #run the second part of the puzzle





if __name__=="__main__":
    main()