import numpy as np
import pyopencl as cl
from PIL import Image

from utils.map_to_mesh import generate_mesh

# === Simulation variables ===
iterations = 100

rain_intensity = "25.0f"

delta_t = "0.0005f"
pipe_cross_section = "0.6f"
pipe_length = "1.0f"
gravity = "9.81f"
cell_distance_x = "1.0f"
cell_distance_y = "1.0f"

sediment_capacity = "0.3f"
dissolving_constant = "0.3f"
erosion_constant = "0.3f"

evaporation_constant = "0.15f"
# =================================


constants_definition = f'''
#define delta_t {delta_t}

#define RAIN_INTENSITY {rain_intensity}

#define A {pipe_cross_section}
#define l {pipe_length}
#define g {gravity}

#define lx {cell_distance_x}
#define ly {cell_distance_y}

#define Ksc {sediment_capacity}
#define Ks {dissolving_constant}
#define Kd {erosion_constant}

#define Ke {evaporation_constant}\n
'''

# Read the kernel code
with open("kernels/1_water_increment.cl", "r") as kernel_file:
    water_increment_kernel = constants_definition + kernel_file.read()

with open("kernels/2_1_update_output_flux.cl", "r") as kernel_file:
    update_output_flux_kernel = constants_definition + kernel_file.read()

with open("kernels/2_2_update_water_surface_velocity.cl", "r") as kernel_file:
    update_water_surface_kernel = constants_definition + kernel_file.read()

with open("kernels/3_erosion_deposition.cl", "r") as kernel_file:
    erosion_deposition_kernel = constants_definition + kernel_file.read()

with open("kernels/4_5_sediment_transport_evaporation.cl", "r") as kernel_file:
    sediment_transport_evaporation_kernel = constants_definition + kernel_file.read()

# Create OpenCL context and command queue
ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

# Load depth map using PIL
depth_map_pil = Image.open("assets/heightmap.jpg")
depth_map_pil = depth_map_pil.convert("L")
depth_map_data = np.array(depth_map_pil).astype(np.float32) / np.float32(255)

map_width = np.int32(depth_map_pil.width)
map_height = np.int32(depth_map_pil.height)

# Load water map
# water_map = np.random.rand(map_width * map_height).astype(np.float32) * 0.01
water_map = np.zeros(map_width * map_height).astype(np.float32)

# Load suspended sediment map
sediment_map = np.zeros(map_width * map_height, dtype=np.float32)

# Load Flux vectors
flux_vectors = np.zeros((map_width * map_height, 4), dtype=cl.cltypes.float(4))

# Load velocity vectors
velocity_vectors = np.zeros((map_width * map_height, 2), dtype=cl.cltypes.float(2))

# Create OpenCL buffers for input and output
depth_map_buffer = [cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=depth_map_data),
                    cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=depth_map_data)]

water_map_buffer = [cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=water_map),
                    cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=water_map)]

sediment_map_buffer = [cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=sediment_map),
                       cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=sediment_map)]

flux_vectors_buffer = [cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=flux_vectors),
                       cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=flux_vectors)]

velocity_vectors_buffer = cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR,
                                    hostbuf=velocity_vectors)

# Compile Kernels
water_increment_program = cl.Program(ctx, water_increment_kernel).build()
update_output_flux_program = cl.Program(ctx, update_output_flux_kernel).build()
update_water_surface_program = cl.Program(ctx, update_water_surface_kernel).build()
erosion_deposition_program = cl.Program(ctx, erosion_deposition_kernel).build()
sediment_transport_evaporation_program = cl.Program(ctx, sediment_transport_evaporation_kernel).build()

# Execute Kernels
global_size = (map_width, map_height)  # size of 2D grid
local_size = None  # let OpenCL choose the work-group size

for i in range(iterations):
    # 3.1 Water Increment
    water_increment_program.waterIncrement(queue, global_size, local_size,
                                           map_width, map_height,
                                           cl.cltypes.int(i),
                                           water_map_buffer[i % 2])

    # 3.2.1 Outflow Flux Computation
    update_output_flux_program.updateOutputFlux(queue, global_size, local_size,
                                                map_width, map_height,
                                                depth_map_buffer[i % 2],
                                                water_map_buffer[i % 2],
                                                flux_vectors_buffer[i % 2],
                                                flux_vectors_buffer[(i + 1) % 2])

    # 3.2.2 Water Surface Velocity Field Update
    update_water_surface_program.updateWaterSurfaceVelocity(queue, global_size, local_size,
                                                            map_width, map_height,
                                                            water_map_buffer[i % 2],
                                                            flux_vectors_buffer[(i + 1) % 2],
                                                            velocity_vectors_buffer)

    # 3.3 Erosion and Deposition
    erosion_deposition_program.erosionDeposition(queue, global_size, local_size,
                                                 map_width, map_height,
                                                 depth_map_buffer[i % 2],
                                                 depth_map_buffer[(i + 1) % 2],
                                                 sediment_map_buffer[i % 2],
                                                 velocity_vectors_buffer)

    # 3.4 Sediment Transportation
    # 3.5 Evaporation
    sediment_transport_evaporation_program.sedimentTransportEvaporation(queue, global_size, local_size,
                                                                        map_width, map_height,
                                                                        water_map_buffer[i % 2],
                                                                        water_map_buffer[(i + 1) % 2],
                                                                        sediment_map_buffer[i % 2],
                                                                        sediment_map_buffer[(i + 1) % 2],
                                                                        velocity_vectors_buffer)

# Read the result
cl.enqueue_copy(queue, depth_map_data, depth_map_buffer[iterations % 2])

array = np.uint8(np.array(depth_map_data * 255).reshape(512, 512))
generate_mesh(depth_map_data, "modified_mesh.obj")
img = Image.fromarray(array, 'L')
img.save("modified_depth_map.jpg")
