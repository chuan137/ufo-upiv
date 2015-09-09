__kernel void found_cand(__global float* input, 
                         __global float* positions, 
                         __global unsigned* counter, 
                         __const float thredshold)
{
    int x = get_global_id(0); //first dimension
    int y = get_global_id(1); //second dimension
    int w = get_global_size(0); //width

    int idx = x + y*w; //get real position
    int old;
    if(input[idx] > thredshold)
    {
        old = atomic_inc(&counter[0]);
        positions[3*old] = (float)x; //save x coordinate
        positions[3*old + 1] = (float)y; //save y coordinate
        positions[3*old + 2] = input[idx];
    }
}
