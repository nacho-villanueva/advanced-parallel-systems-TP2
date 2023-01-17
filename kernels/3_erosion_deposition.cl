float calculateSinAlpha(__global float* depthMap, int x, int y, int mapWidth, int mapHeight) {

	float height_L = (x-1 >= 0) ? 		depthMap[(x-1) + y * mapWidth] : depthMap[x + y * mapWidth];
	float height_R = (x+1 < mapWidth) ? depthMap[(x+1) + y * mapWidth] : depthMap[x + y * mapWidth];
	float height_T = (y-1 >= 0) ? 		depthMap[x + (y-1) * mapWidth] : depthMap[x + y * mapWidth];
	float height_B = (y+1 < mapHeight)? depthMap[x + (y+1) * mapWidth] : depthMap[x + y * mapWidth];

	float deltaHx = (height_L-height_R) / (2.0f * lx / mapWidth);
	float deltaHy = (height_B-height_T) / (2.0f * ly / mapHeight);

	return sqrt(deltaHx*deltaHx + deltaHy*deltaHy) / sqrt(1 + deltaHx*deltaHx + deltaHy*deltaHy);
}

__kernel void erosionDeposition(int mapWidth, int mapHeight,
                                __global float* depthMap,
                                __global float* newDepthMap,
                                __global float* sedimentMap,
                                __global float2* velocityVectors)
{
    int x = get_global_id(0);
    int y = get_global_id(1);
    int index = x + y * mapWidth;

    float sinAlpha = calculateSinAlpha(depthMap, x, y, mapWidth, mapHeight);
    sinAlpha = min(sinAlpha, 0.15f);

    float v_norm = sqrt(velocityVectors[index][0] * velocityVectors[index][0] + velocityVectors[index][1] * velocityVectors[index][1]);

    float C = Ksc * sinAlpha * v_norm;

    if(C > sedimentMap[index]){
        newDepthMap[index] = depthMap[index] + Ks * (C - sedimentMap[index]);
        sedimentMap[index] = sedimentMap[index] + Ks * (C - sedimentMap[index]);
    } else {
        newDepthMap[index] = depthMap[index] + Kd * (C - sedimentMap[index]);
        sedimentMap[index] = sedimentMap[index] - Kd * (C - sedimentMap[index]);
    }

}
