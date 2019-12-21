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
    n_runs=1
    computer = intcode.IntcodeComputer(verbose=False)
    input_path=Path("speed_test.txt")
    int_code=load_commented_program(input_path)
    computer.load_memory(int_code)
    computer.input(n_runs)  #input the number of runs to execute
    computer.run()
    print("program executed")
    #print(computer.program_finished)

    setup_code= '''
from __main__ import load_commented_program
import intcode
import numpy as np
from pathlib import Path
import re

n_runs=1000
computer = intcode.IntcodeComputer(verbose=False)
input_path=Path("speed_test.txt")
int_code=load_commented_program(input_path)
computer.load_memory(int_code)
    '''
    evaluation_code='''
computer.reset()
    '''
    n_repeats=100000
    eval_time=timeit.timeit(evaluation_code, setup=setup_code,number=n_repeats)
    print("{} seconds per iteration".format(eval_time/n_repeats))

if __name__=="__main__":
    main()