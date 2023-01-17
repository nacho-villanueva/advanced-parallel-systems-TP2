float getFluxFromVector(__global float4* fluxVectors, int index, int2 offset) {
    if(index == -1)
        return 0;

    if(offset[0] == -1)
        return fluxVectors[index][0]; // Left
    else if(offset[0] == 1)
        return fluxVectors[index][1]; // Right
    else if(offset[1] == -1)
        return fluxVectors[index][2]; // Top
    else if(offset[1] == 1)
        return fluxVectors[index][3]; // Bottom
    
    return 0;
}

__kernel void updateWaterSurfaceVelocity(int mapWidth, int mapHeight,
                                __global float* waterMap,
                                __global float4* fluxVectors,
                                __global float2* velocityVectors)
{
    int x = get_global_id(0);
    int y = get_global_id(1);
    int index = x + y * mapWidth;

    // Get input flux
    float left_index = (x-1 >= 0) ? (x-1) + y * mapWidth : -1;
    float left_fR = getFluxFromVector(fluxVectors, left_index, (int2)(1, 0));

    float right_index = (x+1 < mapWidth) ? (x+1) + y * mapWidth : -1;
    float right_fL = getFluxFromVector(fluxVectors, right_index, (int2)(-1, 0));

    float top_index = (y-1 >= 0) ? x + (y-1) * mapWidth : -1;
    float top_fB = getFluxFromVector(fluxVectors, top_index, (int2)(0, 1));

    float bottom_index = (y+1 < mapHeight) ? x + (y + 1) * mapWidth : -1;
    float bottom_fT = getFluxFromVector(fluxVectors, bottom_index, (int2)(0, -1));

    // Get output flux
    float fL = getFluxFromVector(fluxVectors, index, (int2)(-1, 0));
    float fR = getFluxFromVector(fluxVectors, index, (int2)(1, 0));
    float fT = getFluxFromVector(fluxVectors, index, (int2)(0, -1));
    float fB = getFluxFromVector(fluxVectors, index, (int2)(0, 1));

    float delta_V = delta_t * ((left_fR + right_fL + top_fB + bottom_fT) - (fL + fR + fT + fB));

    // Update water levels
    float newWaterLevel = (waterMap[index] + delta_V) / (lx * ly);
    float avgWaterLevel = (newWaterLevel + waterMap[index]) / 2; 

    // Update velocity vectors
    if(waterMap[index] > 0.0f) {
        velocityVectors[index][0] = ((left_fR - fL) + (right_fL - fR)) / (waterMap[index] * ly);
        velocityVectors[index][1] = ((top_fB - fT) + (bottom_fT - fB)) / (waterMap[index] * lx);
    } else {
        velocityVectors[index][0] = 0;
        velocityVectors[index][1] = 0;
    }

    waterMap[index] = newWaterLevel;
}
