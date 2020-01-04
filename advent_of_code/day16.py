import numpy as np
from pathlib import Path
from math import ceil

def get_base_pattern(phase_step):
    return np.roll(np.repeat(np.array([0, 1, 0, -1]), phase_step + 1), -1)

def flawed_ft(ft_input=np.array([])):
    # generator to return the fft phase
    output = np.full(ft_input.shape, 0)  # output array that will be filled
    ft_matrix=np.array([
        np.tile(get_base_pattern(step), ceil(ft_input.shape[0] / get_base_pattern(step).shape[0]))[:ft_input.shape[0]]
        for step in range(ft_input.shape[0])
    ])
    while True:
        # every time the generator is called return a new signal output by
        output=np.mod(abs(np.matmul(ft_matrix,ft_input.T)),10) # multiply the input by the ft_matrix operator and keep only the ones digit
        #output = np.array([
        #    np.mod(abs(np.sum(np.multiply(ft_input, pattern_array[step]))), 10)
        #    for step in range(ft_input.shape[0])]) # perform the FFT phase calculation by multiplying and summing
        yield output
        ft_input = output


def fast_fft(fft_input=np.array([])):
    # generator for the fft which is valid only when you care about the latter half of the data
    while True:
        # the fft is the accumulation of the input reversed
        output = np.flip(np.mod(np.cumsum(np.flip(fft_input)), 10))
        yield output
        fft_input = output


def get_input():
    puzzle_input_path = Path("puzzle_inputs") / "day16_input.txt"
    with open(puzzle_input_path) as file:
        puzzle_input = file.readline()  # there's only one line of data
    # puzzle_input = "02935109699940807407585447034323" # test input
    puzzle_input = np.array([int(x) for x in puzzle_input.strip()])  # parse the input and convert to an numpy array
    return puzzle_input


def puzzle_part_a(puzzle_input):
    ft = flawed_ft(puzzle_input)
    for _ in range(99):
        next(ft)
    signal_output = next(ft)[0:8]
    print("output signal is {}".format(''.join([str(j) for j in signal_output])))


def puzzle_part_b(puzzle_input):
    n_repetitions = 10000
    input_length = puzzle_input.shape[0] * n_repetitions
    input_offset = int(''.join([str(j) for j in puzzle_input[:7]]))
    condensed_input_length = input_length - input_offset  # the part of input we actually care to look at
    print('input is {} digits long but answer offset is {} only need to look at last {} digits'.format(input_length,
                                                                                                       input_offset,
                                                                                                       input_length - input_offset))
    quot, rem = divmod(condensed_input_length, puzzle_input.shape[0])
    # print("{},{}".format(quot,rem))
    condensed_input = np.concatenate((puzzle_input[-rem:], np.tile(puzzle_input, quot)))
    # print(condensed_input.shape)
    fft = fast_fft(condensed_input)
    for _ in range(99):
        next(fft)  # iterate 99 steps, only care about 100th
    puzzle_answer = ''.join([str(j) for j in next(fft)[:8]])
    print("Answer is {}".format(puzzle_answer))

def puzzle_tests():
    test_input_string="12345678"
    puzzle_input=np.array([int(x) for x in test_input_string])
    ft = flawed_ft(puzzle_input)
    for _ in range(4):
        print(next(ft))
    signal_output = next(ft)[0:8]
    print("output signal is {}".format(''.join([str(j) for j in signal_output])))
def main():
    puzzle_input = get_input()
    print("\n**Running Test Cases**")
    puzzle_tests()
    print("\n**Running Puzzle Part A**")
    puzzle_part_a(puzzle_input)
    print("\n**Running Puzzle Part B**")
    puzzle_part_b(puzzle_input)


if __name__ == "__main__":
    main()
