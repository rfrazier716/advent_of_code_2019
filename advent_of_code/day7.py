import common_dependencies.intcode as intcode
import numpy as np
from pathlib import Path
import itertools


class Amplifier_array():
    def __init__(self, n_amps, program=[]):
        self._amps = [intcode.IntcodeComputer(program) for _ in range(n_amps)]

    def load_software(self, program):
        [self._amps[j].load_memory(program) for j in range(len(self._amps))]

    def reset(self):
        [self._amps[j].reset() for j in range(len(self._amps))]

    def set_phases(self, phase_array):
        [self._amps[j].input(phase_array[j]) for j in range(len(self._amps))]

    def run(self):
        amplifier_input=0
        for amp in self._amps:
            amp.input(amplifier_input)  #provide input to the amp
            amp.run()   # run until the program terminates
            amplifier_input=amp.flush_output()[-1]  # the input for the next amp is the output of the previous amp
        return amplifier_input  #the input going to the thruster is the output of the final amplifer

    def run_with_feedback(self):
        amplifier_input = 0
        thruster_input = 0
        try:
            while True:
                for amp in self._amps:
                    amp.input(amplifier_input)  # provide input to the amp
                    amp.resume()  # run until the program stops
                    amplifier_input = amp.flush_output()[-1]  # the input for the next amp is the output of the previous amp
                thruster_input=amplifier_input  #the thruster input is the value coming from the final amp
        except IndexError: # Continue to loop until an amplifier stops providing output
            return thruster_input



def puzzle_part_a(amps):
    thruster_max=0
    max_thruster_permutation=(0,0)
    for permutation in itertools.permutations(range(5)):
        amps.reset()
        amps.set_phases(permutation)
        thruster_input=amps.run()
        if thruster_input>thruster_max:
            thruster_max=thruster_input
            max_thruster_permutation=permutation
    print("Max thrust is {} with phase setting {}".format(thruster_max,max_thruster_permutation))

def puzzle_part_b(amps):
    thruster_max=0
    max_thruster_permutation=(0,0)
    for permutation in itertools.permutations(range(5,10)):
        amps.reset()
        amps.set_phases(permutation)
        thruster_input=amps.run_with_feedback()
        if thruster_input>thruster_max:
            thruster_max=thruster_input
            max_thruster_permutation=permutation
    print("Using Feedback, Max thrust is {} with phase setting {}".format(thruster_max,max_thruster_permutation))

def main():
    input_path = Path("puzzle_inputs") / "day7_input.txt"
    amp_software = np.loadtxt(input_path, delimiter=",", dtype=int)
    amps = Amplifier_array(5,amp_software)
    puzzle_part_a(amps)
    puzzle_part_b(amps)


if __name__ == "__main__":
    main()
