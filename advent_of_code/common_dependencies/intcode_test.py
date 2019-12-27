import intcode
import numpy as np
from pathlib import Path
import re
import timeit


def load_commented_program(file_path):
    with open(file_path) as file:
        int_code=re.findall("[0-9]+",",".join([line.split("#")[0] for line in file.readlines()])) #pull int code as a string
        return np.array([int(num) for num in int_code])   #return int_code as a numpy array



def main():
    n_runs=100
    computer = intcode.IntcodeComputer(verbose=True)
    input_path=Path("speed_test.txt")
    int_code=load_commented_program(input_path)
    computer.load_memory(int_code)
    computer.input(n_runs)  #input the number of runs to execute
    computer.run()
    print(computer.memory)
    print("program executed")
    #print(computer.program_finished)

if __name__=="__main__":
    main()