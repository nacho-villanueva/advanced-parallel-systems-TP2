__kernel void sedimentTransportEvaporation(int mapWidth, int mapHeight,
                                __global float* waterMap,
                                __global float* newWaterMap,
                                __global float* sedimentMap,
                                __global float* newSedimentMap,
                                __global float2* velocityVectors)
{
    int x = get_global_id(0);
    int y = get_global_id(1);
    int index = x + y * mapWidth;

    // Sediment Transport
    // Step backwards in time
    float x_step = clamp(x - velocityVectors[index][0] * delta_t, 0.0f, (float)mapWidth-1);
    float y_step = clamp(y - velocityVectors[index][1] * delta_t, 0.0f, (float)mapHeight-1);

    // Interpolate
    float s1 = sedimentMap[(int)(floor(x_step) + floor(y_step) * mapWidth)];
    float s2 = sedimentMap[(int)(ceil(x_step) + floor(y_step) * mapWidth)];
    float s3 = sedimentMap[(int)(floor(x_step) + ceil(y_step) * mapWidth)];
    float s4 = sedimentMap[(int)(ceil(x_step) + ceil(y_step) * mapWidth)];

	float s12 = (x_step - floor(x_step)) * s2 + (ceil(x_step) - x_step) * s1;
	float s34 = (x_step - floor(x_step)) * s4 + (ceil(x_step) - x_step) * s3;

	newSedimentMap[index] = (y_step - floor(y_step)) * s12 + (ceil(y_step) - y_step) * s34;
    
    // Evaporation
    newWaterMap[index] = max(waterMap[index] * (1 - Ke * delta_t), 0.0f);
}
