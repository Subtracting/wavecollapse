
# 1. Read the input bitmap and count NxN patterns.
#     (optional) Augment pattern data with rotations and reflections.
# 2. Create an array with the dimensions of the output (called "wave" in the source). 
#     Each element of this array represents a state of an NxN region in the output. 
#     A state of an NxN region is a superposition of NxN patterns of the input with boolean coefficients (so a state of a pixel in the output is a superposition of input colors with real coefficients). 
#     False coefficient means that the corresponding pattern is forbidden, true coefficient means that the corresponding pattern is not yet forbidden.
# 3. Initialize the wave in the completely unobserved state, i.e. with all the boolean coefficients being true.
# 4. Repeat the following steps:
#    i. Observation:
#       a. Find a wave element with the minimal nonzero entropy. 
#          If there is no such elements (if all elements have zero or undefined entropy) then break the cycle (4) and go to step (5).
#       b. Collapse this element into a definite state according to its coefficients and the distribution of NxN patterns in the input.
#    ii. Propagation: propagate information gained on the previous observation step.
# 5. By now all the wave elements are either in a completely observed state (all the coefficients except one being zero) or in the contradictory state (all the coefficients being zero). 
#       In the first case return the output. 
#       In the second case finish the work without returning anything.


from PIL import Image
from numpy import asarray, array
from collections import defaultdict
from math import log10, log2
from random import choices
from matplotlib import cm
import sys

sys. setrecursionlimit(10000)

def calc_entropy(x, y, super_array):
  weights = super_array[x][y][1].values()
  sum_weights = sum(weights)
  sum_log_weights = sum([weight * log10(weight) for weight in weights])

  entropy = log10(sum_weights) - (sum_log_weights / sum_weights)

  return entropy


def min_entropy(super_array):
    global entropy_value

    min_entropy = 999
    min_entropy_coords = (99, 99)
    for x in range(dimension_x):
        for y in range(dimension_y):
            if (x, y) not in collapsed_cells:
                entropy_pixel = calc_entropy(x, y, super_array)
                entropy_array[x][y] = entropy_pixel
                if entropy_pixel < min_entropy:
                    min_entropy = entropy_pixel
                    min_entropy_coords = (x, y)
                    print("min entropy: ", min_entropy, min_entropy_coords)
    
    if min_entropy_coords == (99, 99):
        entropy_value = False

    return min_entropy_coords


def process_pixel(img_arr, x, y):
    r, g, b, a = img_arr[x, y]
    pixel = (r, g, b)

    return pixel

def propagate(x, y, super_array, possible_adjacent_states):

    # bottom
    if y + 1 < dimension_y and (x, y + 1) not in seen_cells and (x, y + 1) not in collapsed_cells:
        # print("bottom", (x, y + 1))
        seen_cells.append((x, y + 1))
        possible_states = adjust_state(x, y + 1, super_array, possible_adjacent_states)
        propagate(x, y + 1, super_array, possible_states)

    # top
    if y - 1 >= 0 and (x, y - 1) not in seen_cells and (x, y - 1) not in collapsed_cells:
        # print("top", (x, y - 1))
        seen_cells.append((x, y - 1))
        possible_states = adjust_state(x, y - 1, super_array, possible_adjacent_states)
        propagate(x, y - 1, super_array, possible_states)

    # left
    if x - 1 >= 0 and (x - 1, y) not in seen_cells and (x - 1, y) not in collapsed_cells:
        # print("left", (x - 1, y))
        seen_cells.append((x - 1, y))
        possible_states = adjust_state(x - 1, y, super_array, possible_adjacent_states)
        propagate(x - 1, y, super_array, possible_states)

    # right
    if x + 1 < dimension_x and (x + 1, y) not in seen_cells and (x + 1, y) not in collapsed_cells:
        # print("right", (x + 1, y))
        seen_cells.append((x + 1, y))
        possible_states = adjust_state(x + 1, y, super_array, possible_adjacent_states)
        propagate(x + 1, y, super_array, possible_states)


def adjust_state(x, y, super_array, possible_adjacent_states):
    wavefunction_choice = {k: v for k, v in super_array[x][y][0].items() if k in possible_adjacent_states}
    weight_choice = {k: v for k, v in super_array[x][y][1].items() if k in possible_adjacent_states}
    super_array[x][y] = [wavefunction_choice, weight_choice]

    possible_states = [list(s)[i] for s in list(wavefunction_choice.values()) for i in range(len(s))]

    return possible_states


def collapse(x, y, super_array):
    pixel_collapse = super_array[x][y]
    state_choice = choices(population=list(pixel_collapse[1].keys()),
                            weights=list(pixel_collapse[1].values()),
                            k=1)
    
    print(state_choice, super_array[x][y])
    collapsed_cells.append((x, y))
    
    possible_adjacent_states = adjust_state(x, y, super_array, possible_adjacent_states=state_choice)

    propagate(x, y, super_array, possible_adjacent_states)
    
    # propagate function across all pixels
    # VERDER - in sequentie propageren?

    return super_array[x][y]

def adj_pixel_pairs(img_arr):
    distinct_pairs = defaultdict(set)
    weights = defaultdict(int)
    
    for x in range(width):
        for y in range(height):

            pixel = process_pixel(img_arr, x, y)

            weights[pixel] += 1 / (width*height)
 
            # bottom
            if y + 1 < height:
                pair_pixel = process_pixel(img_arr, x, y + 1)
                distinct_pairs[pixel].add(pair_pixel)
            
            # top
            if y - 1 >= 0:
                pair_pixel = process_pixel(img_arr, x, y - 1)
                distinct_pairs[pixel].add(pair_pixel)

            # left
            if x - 1 >= 0:
                pair_pixel = process_pixel(img_arr, x - 1, y)
                distinct_pairs[pixel].add(pair_pixel)

            # right
            if x + 1 < width:
                pair_pixel = process_pixel(img_arr, x + 1, y)
                distinct_pairs[pixel].add(pair_pixel)

    return distinct_pairs, weights

dimension_x = 20
dimension_y = 20

name = 'cat'
image_src = f'.\images\{name}.png'
image = Image.open(image_src)
img_arr = asarray(image)

width, height, rgb_size = img_arr.shape

wavefunction, weights = adj_pixel_pairs(img_arr)

super_array = [[[wavefunction, weights] for _ in range(dimension_x)] for _ in range(dimension_y)]
entropy_array = [[999 for _ in range(dimension_x)] for _ in range(dimension_y)]

collapsed_cells = []
entropy_value = True

rgb_array = [[[(0,0,0)] for _ in range(dimension_x)] for _ in range(dimension_y)]

while True:
    seen_cells = []

    collapse_x, collapse_y = min_entropy(super_array)

    if entropy_value == False:
        break

    collapse(collapse_x, collapse_y, super_array)

    # print(super_array)



    for x in range(dimension_x):
        for y in range(dimension_y):
            pixel_wf = super_array[x][y][1].keys()
            for key in pixel_wf:
                rgb_array[x][y] = key

    # print(rgb_array)


    im = Image.fromarray(array(rgb_array), 'RGB')

    im.save(f"wavefunc_{name}_{dimension_x}.png")