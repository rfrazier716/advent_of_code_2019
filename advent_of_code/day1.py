import numpy as np
from pathlib import Path


def required_fuel(mass):
    # Defined in the puzzle for the amount of fuel required for a given mass
    return max(np.floor(mass / 3) - 2, 0)


def required_fuel_recursive(mass):
    additional_fuel = required_fuel(mass)
    total_fuel = additional_fuel
    while additional_fuel > 0:
        additional_fuel = required_fuel(additional_fuel)
        total_fuel += additional_fuel
    return total_fuel


def calculate_fuel_requirements(masses):
    # Part 1 -- Calculating total fuel needed for the list of modules
    vfunc=np.vectorize(required_fuel)
    total_fuel = np.sum(vfunc(masses))
    # Part 2 -- Recursively Calculating the total fuel needed
    vfunc=np.vectorize(required_fuel_recursive)
    total_fuel_recursive = np.sum(vfunc(masses))

    print("Total Fuel for all modules:\t{}".format(total_fuel))
    print("Total Fuel Accounting for weight of Fuel:\t{}".format(total_fuel_recursive))


def main():
    puzzle_input_file = Path("puzzle_inputs") / "day1_input.txt"
    masses = np.loadtxt(puzzle_input_file)
    #masses = np.array([100756])
    calculate_fuel_requirements(masses)


if __name__ == "__main__":
    main()
