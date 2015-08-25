kernel void
likelihood (global float *output, 
            read_only image2d_t input, 
            constant int *mask,
            private int maskSize)
{
    const sampler_t smp = CLK_NORMALIZED_COORDS_FALSE |
                          CLK_ADDRESS_CLAMP_TO_EDGE |
                          CLK_FILTER_NEAREST;

    int2 here = (int2) (get_global_id (0), get_global_id (1));
}
