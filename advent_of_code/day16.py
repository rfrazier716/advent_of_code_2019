import numpy as np
from pathlib import Path
from math import ceil

def flawed_ft(input=np.array([])):
    #generator to return the fft phase
    base_pattern=np.array([0,1,0,-1])   # base pattern of the FFT
    phase_pattern=[np.roll(np.ravel(np.vstack([base_pattern for _ in range(step+1)]),"F"),-1) for step in range(len(input))]
    output=np.full(input.shape,0)   # output array that will be filled
    while True:
        for step in range(len(input)):
            base_pattern=np.roll(np.repeat([0,1,0,-1],step+1),-1)
            pattern_array=np.tile(base_pattern,ceil(input.shape[0]/base_pattern.shape[0]))[:len(input)] #build the appropriate pattern array
            output[step]=int(str(np.sum(np.multiply(input,pattern_array)))[-1])  # keep only the ones digit
        yield output
        input=output

def get_input():
    puzzle_input_path = Path("puzzle_inputs") / "day16_input.txt"
    with open(puzzle_input_path) as file:
        input=file.readline()   #there's only one line of data
    input = np.array([int(x) for x in input.strip()])   # parse the input and convert to an numpy array
    return input

def puzzle_part_a(puzzle_input):
    ft=flawed_ft(puzzle_input)
    for _ in range(99):
        next(ft)
    signal_output=next(ft)[0:8]
    print("output signal is {}".format(''.join([str(j) for j in signal_output])))

def main():
    puzzle_input = get_input()
    print("\n**Running Puzzle Part A**")
    print(len(puzzle_input))
    puzzle_part_a(puzzle_input)

if __name__=="__main__":
    main()
