import numpy as np
from pathlib import Path
import itertools

import common_dependencies.intcode as intcode

def process_int_code(int_code):
    int_code[1]=12 #replace position 1 with value 1
    int_code[2]=2 #replace position 2 with value 2
    computer=intcode.IntcodeComputer()
    computer.load_memory(int_code)
    mem_result=computer.run()
    return mem_result[0]

def find_noun_verb_combo(int_code):
    for noun,verb in itertools.product(range(100),range(100)):
        int_code[1]=noun #assign the noun
        int_code[2]=verb #assign the verb
        computer = intcode.IntcodeComputer()
        computer.load_memory(int_code)
        mem_result=computer.run()
        if mem_result[0]==19690720:
            print("Using input of noun={} and verb={} gives valid result, puzzle solution is {}".format(noun,verb,100*noun+verb))

def main():
    #load int code from file
    puzzle_input_path=Path("puzzle_inputs") / "day2_input.txt"
    int_code=np.loadtxt(puzzle_input_path, delimiter=",",dtype=int)
    result=process_int_code(int_code)
    print(result)
    find_noun_verb_combo(int_code)

if __name__=="__main__":
    main()