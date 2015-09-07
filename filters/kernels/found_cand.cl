__kernel void found_cand(__global float* input,__global int* positions, __global unsigned* counter)
{
    int x = get_global_id(0); //first dimension
    int y = get_global_id(1); //second dimension
    int w = get_global_size(0); //width


    int idx = x + y*w; //get real position
    int old;
    if(input[idx] > 0.0)
    {
        old = atomic_inc(&counter[0]);
        positions[old << 1] = x; //save x coordinate
        positions[(old << 1) + 1] = y; //save y coordinate
    }








}
