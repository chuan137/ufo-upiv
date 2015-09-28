__kernel void found_cand(__global float* input, 
                         __global float* output, 
                         __global int *counter,
                         __const float thredshold,
                         __const unsigned n)
{
    int x = get_global_id(0); //first dimension
    int y = get_global_id(1); //second dimension
    int w = get_global_size(0); //width
    int s = get_global_size(1) * w;
    
    int idx = x + y*w + n*s; //get real position
    int old;
    if(input[idx] > thredshold)
    {
        old = atomic_inc(counter);
        output[5*old + 0] = (float)x; //save x coordinate
        output[5*old + 1] = (float)y; //save y coordinate
        output[5*old + 2] = (float)n;
        output[5*old + 3] = input[idx];
        output[5*old + 4] = (float)1;
    }
}
