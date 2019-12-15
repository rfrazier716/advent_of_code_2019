import numpy as np


def number_contains_duplicate(number):
    # turns number int a numpy array and subtracts itself shifted 1 position to the right, if a zero exists in the resulting array the number has consecutive duplicates
    number_arr = np.array([int(d) for d in str(number)], dtype=int)
    return np.isin(0, np.subtract(number_arr, np.roll(number_arr, 1))[1:])


def number_contains_double_pair(number):
    # checks if only a double exists in the number, returns false if 3 or more occurrences
    number_arr = np.array([0]+[int(d) for d in str(number)], dtype=int)
    differences=np.diff(number_arr)
    accumulated_arr=np.add.accumulate(differences)
    try:
        return np.isin(2,np.bincount(accumulated_arr))
    except ValueError:
        return None


def number_in_ascending_order(number):
    number_arr = np.array([int(d) for d in str(number)], dtype=int)
    return all([number_arr[j]<=number_arr[j+1] for j in range(len(number_arr)-1)])

def solve_puzzle_set():
    number_range = [353096, 843212]
    multi_count = 0
    double_count = 0
    for number in range(*number_range):
        if number_in_ascending_order(number):
            if number_contains_duplicate(number):
                multi_count += 1
                if number_contains_double_pair(number):
                    double_count += 1
    print("part A: {}\npart B: {}".format(multi_count, double_count))

def test_cases():
    test_numbers=[111111,112222,124789,112233,123444,111122]
    for number in test_numbers:
        asc=number_in_ascending_order(number)
        set=number_contains_duplicate(number)
        dbl=number_contains_double_pair(number)
        print("{}, asc:{},set:{},double: {}".format(number,asc,set,dbl))

def main():
    test_cases()
    print("Running through puzzle set range")
    solve_puzzle_set()



if __name__ == "__main__":
    main()
