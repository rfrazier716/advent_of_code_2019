import intcode
import numpy as np
from pathlib import Path

def main():
    computer = intcode.IntcodeComputer(verbose=False)
    input_path=Path("test_inputs.txt")
    int_code = np.loadtxt(input_path, delimiter=",", dtype=int)
    for j in range(10):
        computer.load_memory(int_code)
        computer.input(j)
        computer.run()
        print("Input: {}\tOutput: {}".format(j,computer.flush_output()))
    print(computer.memory)


if __name__=="__main__":
    main()