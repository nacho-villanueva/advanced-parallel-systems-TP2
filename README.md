
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
    
## Usage/Examples
In order to execute the script, you simply have to run the main.py script. At the top of the script
you will be able to find all the adjustable parameters.

In the utils directory there are also some functions which serve to generate a procedural height map
or turning a height map into an OBJ mesh file.


## References
1. Xing Mei, Philippe Decaudin, Bao-Gang Hu. Fast Hydraulic Erosion Simulation and Visualization
on GPU. PG ’07 - 15th Pacific Conference on Computer Graphics and Applications, Oct 2007, Maui,
United States. [https://hal.inria.fr/inria-00402079/document]

2. https://huw-man.github.io/Interactive-Erosion-Simulator-on-GPU/