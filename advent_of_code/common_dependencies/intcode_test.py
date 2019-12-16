import intcode
import numpy as np
from pathlib import Path

def main():
    computer = intcode.IntcodeComputer(verbose=True)
    input_path=Path("test_inputs.txt")
    int_code = np.loadtxt(input_path, delimiter=",", dtype=np.int64)
    computer.load_memory(int_code)
    computer.run()
    print(computer.flush_output())
    print(computer.program_finished)


if __name__=="__main__":
    main()