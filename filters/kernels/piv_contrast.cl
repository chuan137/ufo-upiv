__kernel void 
sigmoid (__global float* res, __global float* data, float mean, float sigma, 
                  float gamma, float c1, float c2, float c3, float c4)
{
    float f1, f2; 

//    ;float c1 = -0.25; // lower threshold
//    ;float c2 = 10;  // higher threshold
//    ;float c3 = 4.0; // shift of sigmoid (in unit of sigma)
//    ;float c4 = 2.0; // width of sigmoid (in unit of sigma)

    int id = get_global_id(0);

    if (data[id] < mean - c1*sigma || data[id] > mean + c2*sigma) {
        f1 = 0.0;
    } else {
        f1 = exp( (mean + c3 * sigma - data[id]) / (c4 *sigma) );
        f1 = 1.0f / (1.0f + f1);
        f2 = pow(data[id], gamma);
    }

    res[id] = f1*f2;
}
