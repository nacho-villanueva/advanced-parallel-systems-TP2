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

float calculateOutflowFlux(int mapWidth, int mapHeight, 
                            __global float* depthMap, __global float* waterMap, 
                            __global float4* fluxVectors, 
                            int2 currentPos, int2 offset) {
    
    if(currentPos[0] + offset[0] >= mapWidth || currentPos[0] + offset[0] < 0 || currentPos[1] + offset[1] >= mapHeight || currentPos[1] + offset[1] < 0)
        return 0;

    int currentIndex = currentPos[0] + currentPos[1] * mapWidth;
    int offsetIndex = currentPos[0] + offset[0] + (currentPos[1] + offset[1]) * mapWidth;

    float delta_h = depthMap[currentIndex] + waterMap[currentIndex] - depthMap[offsetIndex] - waterMap[offsetIndex];

    float new_f = getFluxFromVector(fluxVectors, currentIndex, offset) + delta_t * A * g * delta_h / l;

    return max(0.0f, new_f); 
}

__kernel void updateOutputFlux(int mapWidth, int mapHeight, 
                                __global float* depthMap,
                                __global float* waterMap,
                                __global float4* fluxVectors,
                                __global float4* outputFlux)
{
    int x = get_global_id(0);
    int y = get_global_id(1);
    int index = x + y * mapWidth;

    float fL = calculateOutflowFlux(mapWidth, mapHeight, depthMap, waterMap, fluxVectors, (int2)(x, y), (int2)(-1, 0));
    float fR = calculateOutflowFlux(mapWidth, mapHeight, depthMap, waterMap, fluxVectors, (int2)(x, y), (int2)(1, 0));
    float fT = calculateOutflowFlux(mapWidth, mapHeight, depthMap, waterMap, fluxVectors, (int2)(x, y), (int2)(0, -1));
    float fB = calculateOutflowFlux(mapWidth, mapHeight, depthMap, waterMap, fluxVectors, (int2)(x, y), (int2)(0, 1));

    outputFlux[index] = (float4)(fL, fR, fT, fB);

    float fluxSum = fL + fR + fT + fB;
    
    if(waterMap[index] < fluxSum){
        float K = min(waterMap[index] / (fluxSum * delta_t), 1.0f);
        outputFlux[index] *= K;
    }
}
