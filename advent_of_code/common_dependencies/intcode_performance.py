import re
import numpy as np
import timeit

def load_commented_program(file_path):
    with open(file_path) as file:
        int_code=re.findall("[0-9]+",",".join([line.split("#")[0] for line in file.readlines()])) #pull int code as a string
        return np.array([int(num) for num in int_code])   #return int_code as a numpy array

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

evaluation_code_reset='''
computer.reset()
'''

evaluation_code_program='''
computer.reset()
computer.input(100)
computer.run()
'''

if __name__=="__main__":
    n_repeats=100000
    eval_time=timeit.timeit(evaluation_code_reset, setup=setup_code,number=n_repeats)
    print("resetting computer took {:.03e} seconds per iteration".format(eval_time/n_repeats))
    n_repeats=1000
    eval_time = timeit.timeit(evaluation_code_program, setup=setup_code, number=n_repeats)
    print("running intcode test software took {:.03e} seconds per iteration".format(eval_time / n_repeats))