
#define PHI 1.61803398874f  // Golden Ratio

#define CIRCLE_CENTER (float2)(100.0f, 100.0f)

float goldNoise(float2 xy, float seed){
    float a = tan( distance(xy*PHI, xy) * seed) * xy[0];
    return a - floor(a) ;
}

float wholeMapRain(int2 xy, float seed) {
    float2 fxy = (float2)((float) xy[0], (float) xy[1]);
    return goldNoise(fxy, seed);
}

float circleRain(int2 xy) {
    float2 fxy = (float2)((float) xy[0], (float) xy[1]);
    return (distance(fxy, CIRCLE_CENTER) < 35) ? 1 : 0;
}

__kernel void waterIncrement(int mapWidth, int mapHeight, int iteration, 
                                __global float* waterMap) {
    int x = get_global_id(0);
    int y = get_global_id(1);
    int index = x + y * mapWidth;
    //waterMap[index] += circleRain((int2)(x, y)) * RAIN_INTENSITY * delta_t;
    waterMap[index] += wholeMapRain((int2)(x, y), iteration % 1000) * RAIN_INTENSITY * delta_t;
}