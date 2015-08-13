__kernel void cut(__global float* in_mem, global float* out_mem, float sigma_top, float sigma_bottom)
{
    int id = get_global_id(0);


    //Within the threshold
    if((in_mem[id] <  sigma_top) &&  (in_mem[id] > sigma_bottom))
    {
        out_mem[id] = in_mem[id];
    } 
     else
    {
        out_mem[id] = 0;
    }


}
