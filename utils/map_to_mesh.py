"""
Code taken from:
https://github.com/LoaDy588/py_terrain_mesh
"""

from utils.generate_map import generate_heightmap, export_norm_map

MAP_SIZE = (512, 512)
SCALE = 256
EXPO_HEIGHT = 2

lut_vectors = (
    (-1, 1), (0, 1), (1, 1),
    (-1, 0), (1, 0),
    (-1, -1), (0, -1), (1, -1)
)


def out_of_bounds(coord):
    if coord[0] < 0 or coord[0] >= MAP_SIZE[0]:
        return True
    if coord[1] < 0 or coord[1] >= MAP_SIZE[1]:
        return True
    return False


def generate_vertices(heightmap):
    vertices = []
    base = (-1, -0.75, -1)
    size = 2
    max_height = 0.5
    step_x = size / (MAP_SIZE[0] - 1)
    step_y = size / (MAP_SIZE[1] - 1)

    for x in range(MAP_SIZE[0]):
        for y in range(MAP_SIZE[1]):
            x_coord = base[0] + step_x * x
            y_coord = base[1] + max_height * heightmap[x][y]
            z_coord = base[2] + step_y * y
            vertices.append((x_coord, y_coord, z_coord))
    print("Vertices generated")
    return vertices


def generate_tris():
    edges = []
    surfaces = []

    for x in range(MAP_SIZE[0] - 1):
        for y in range(MAP_SIZE[1] - 1):
            base = x * MAP_SIZE[0] + y
            a = base
            b = base + 1
            c = base + MAP_SIZE[0] + 1
            d = base + MAP_SIZE[0]
            edges.append((a, b))
            edges.append((b, c))
            edges.append((c, a))
            edges.append((c, d))
            edges.append((d, a))
            surfaces.append((a, b, c))
            surfaces.append((a, c, d))
    print("Edges, surfaces generated")
    return edges, surfaces


def export_obj(vertices, tris, filename):
    file = open(filename, "w")
    for vertex in vertices:
        file.write("v " + str(vertex[0]) + " " + str(vertex[1]) + " " + str(vertex[2]) + "\n")
    for tri in tris:
        file.write("f " + str(tri[2] + 1) + " " + str(tri[1] + 1) + " " + str(tri[0] + 1) + "\n")
    file.close()
    print(filename, "saved")
    return


def generate_mesh(height_map, output):
    vertices = generate_vertices(height_map)
    edges, surfaces = generate_tris()
    export_obj(vertices, surfaces, output)


def main():
    heightmap = generate_heightmap()
    generate_mesh(heightmap, "../assets/original_mesh.obj")
    export_norm_map(heightmap, "../assets/heightmap.jpg")


if __name__ == "__main__":
    main()
