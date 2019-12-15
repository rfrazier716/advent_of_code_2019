import intcode
import numpy as np
from pathlib import Path

def main():
    computer = intcode.IntcodeComputer(verbose=False)
    input_path=Path("test_inputs.txt")
    int_code = np.loadtxt(input_path, delimiter=",", dtype=int)
    computer.load_memory(int_code)
    computer.run()
    print(computer.flush_output())
    computer.input(3)
    computer.resume()
    print(computer.flush_output())
    computer.resume()
    computer.resume()
    computer.reset()
    computer.input(3)
    computer.run()
    print(computer.flush_output())


if __name__=="__main__":
    main()