import numpy as np
from pathlib import Path
import itertools
from PIL import Image


class SIF():
    def __init__(self, rows, columns, image_data):
        self._rows = rows
        self._columns = columns
        self._data = image_data

        self._px_per_layer = self._rows * self._columns  # This is how many layers are in the object
        self._n_layers = round(len(image_data) / self._px_per_layer)
        self._layers = np.reshape(image_data, (-1, rows, columns))
        self.render()

    def display_layers(self):
        for layer in self._layers:
            print(layer)

    def layer_checksum(self):
        # returns the number of zeros in each layer
        checksum_arr = []
        for layer in self._layers:
            checksum_arr.append(np.count_nonzero(layer == 0))
        return checksum_arr

    def get_image_layer(self, layer):
        return self._layers[layer]

    def render(self):
        self._image = np.full((self._rows, self._columns),
                           0)  # make an array that defaults to all black the size of the final image
        for row, column in itertools.product(range(self._rows), range(self._columns)):
            # pull the entire z dimension at a specific row/column index
            layer_stack=self._layers[:, row, column]
            self._image[row, column] = str(layer_stack[np.nonzero(self._layers[:, row, column] != 2)[0][0]])
        print(self._image)

    def show(self):
        print(self._image)


def evaluate_test_cases():
    test_cases = ["0222112222120000"]
    for case in test_cases:
        image_data = np.array([int(n) for n in case])
        image = SIF(2,2, image_data)
        image.show()


def get_image_data(file_path):
    with open(file_path) as file:
        image_data = np.array([int(n) for n in ''.join(file.readlines()).strip()])
    return image_data


def puzzle_part_a(image):
    active_layer = image.get_image_layer(np.argmin(image.layer_checksum()))  # returns the layer with the fewest zeros
    n_ones, n_twos = [np.count_nonzero(active_layer == j) for j in [1, 2]]
    print("puzzle answer is: {}".format(n_ones * n_twos))

def puzzle_part_b(image):
    image.show()


def main():
    puzzle_input_path = Path("puzzle_inputs") / "day8_input.txt"
    image_data = get_image_data(puzzle_input_path)
    evaluate_test_cases()

    n_columns = 25
    n_rows = 6
    image = SIF(n_rows, n_columns, image_data)
    puzzle_part_a(image)
    image.show()


if __name__ == "__main__":
    main()
