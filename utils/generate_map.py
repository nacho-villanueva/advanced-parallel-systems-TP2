"""
Code taken from:
https://github.com/LoaDy588/py_terrain_mesh
"""

import random

import noise
import numpy as np
from PIL import Image, ImageDraw

MAP_SIZE = (512, 512)
SCALE = 256
EXPO_HEIGHT = 2


def update_point(coords, seed):
    return noise.snoise2(coords[0] / SCALE,
                         coords[1] / SCALE,
                         octaves=6,
                         persistence=0.5,
                         lacunarity=2,
                         repeatx=MAP_SIZE[0],
                         repeaty=MAP_SIZE[1],
                         base=330
                         )


def normalize(input_map, minimum, maximum, expo):
    scale = maximum - minimum
    output_map = np.zeros(MAP_SIZE)
    for x in range(MAP_SIZE[0]):
        for y in range(MAP_SIZE[1]):
            output_map[x][y] = ((input_map[x][y] - minimum) / scale) ** expo
    return output_map


def generate_heightmap():
    seed = int(random.random() * 1000)
    minimum = 0
    maximum = 0
    heightmap = np.zeros(MAP_SIZE)

    for x in range(MAP_SIZE[0]):
        for y in range(MAP_SIZE[1]):
            new_value = update_point((x, y), seed)
            heightmap[x][y] = new_value
            if new_value < minimum:
                minimum = new_value
            if new_value > maximum:
                maximum = new_value
    print("Height map generated with seed:", seed)
    return normalize(heightmap, minimum, maximum, EXPO_HEIGHT)


def export_norm_map(norm_map, filename):
    image = Image.new('RGB', MAP_SIZE, 0)
    draw = ImageDraw.ImageDraw(image)

    for x in range(MAP_SIZE[0]):
        for y in range(MAP_SIZE[1]):
            color = int(norm_map[x][y] * 255)
            draw.point((x, y), (color, color, color))
    image.save(filename)
    print(filename, "saved")
    return
