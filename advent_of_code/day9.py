import numpy as np
from pathlib import Path
import common_dependencies.intcode as intcode


def main():
    input_path = Path("puzzle_inputs") / "day9_input.txt"
    program = np.loadtxt(input_path, delimiter=",", dtype=np.int64)
    computer=intcode.IntcodeComputer(program,verbose=False)
    computer.input(2)
    print("Running Program")
    computer.run()
    print("Complete!")
    print(computer.flush_output())



if __name__ == "__main__":
    main()