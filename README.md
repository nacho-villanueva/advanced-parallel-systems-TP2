
# Hydraulic Erosion Simulation with OpenCL
#### by Ignacio Villanueva

This is a project which tries to achieve a hydraulic erosion simulation using
OpenCL. The main focus of the project was to explore the possibilities of OpenCL
and how an algorithm could be parallalized.




## Installation

In order to install you will first need to have an OpenCL enabled device with its correct drivers.
This is very OS and CPU/GPU dependent, therefore in order to find your correct Installation method please google search for:
"OpenCL installation" followed by your OS and Device (ex: Intel CPU or NVIDIA GTX 1080)

Once installed you can install the python requirements by running the following command
```bash
  pip install requirements.txt
```
    
## Usage
In order to execute the script, you simply have to run the main.py script. At the top of the script
you will be able to find all the adjustable parameters.

In the utils directory there are also some functions which serve to generate a procedural height map
or turning a height map into an OBJ mesh file.


## Parallalization with OpenCL

The algorithm consists in 5 main steps:
1. Water Increment
2. Outflow Flux Computation
3. Water Surface and Velocity Field Update
4. Erosion and Deposition
5. Sediment Transportation and Water Evaporation
 
  
Each step is better described in the paper referenced below, but our main focus is the parallalization of these steps.
Each of these step will affect one of the corresponding buffers, and in order to avoid race conditions we have to wait for each step to finish
in order to move on. Each of these steps are in charge of calculating several complex calculations per pixel. Thanks to the parallalization, though the
computation is large and complex, the algorithm is able to achieve around 1000 iterations in less than 5 seconds.
Thanks to OpenCL being a crossplatform framework, the execution is not dependant of the device it runs on.
## Problems Faced
1) Particle Based vs Cell Based: In erosion simulation there are 2 main proposals. The first is to generate several particles and follow them down a slope calculating the sediment they erode and where they settle. This is the more intuitive approach to this problem, but not the most parallizable. When going into the details of the algorithm I found there where several barriers which ended up in race conditions, or making the parallalization not very effective. This is the main reason why I've opted to use a Cell based simulation.
2) Scope: Considering the objective of this project, which is to explore parallel systems, the scope of the algorithm chosen tended to shadow the project's objective. The complex mathematics and variety of variables affected resulted being more of a problem than learning OpenCL.
3) Debugging: Debugging parallel systems resulted being quite complex. Different to sequential code, in a parallel system you cannot try to debug line by line, how you would do in a normal system, which resulted in having to concur to more creative ways to debug the system.
## References
[1] Xing Mei, Philippe Decaudin, Bao-Gang Hu. Fast Hydraulic Erosion Simulation and Visualization
on GPU. PG ’07 - 15th Pacific Conference on Computer Graphics and Applications, Oct 2007, Maui,
United States. [https://hal.inria.fr/inria-00402079/document]

[2] https://huw-man.github.io/Interactive-Erosion-Simulator-on-GPU/
