const sampler_t smp = CLK_NORMALIZED_COORDS_FALSE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_NEAREST;

kernel void
likelihood (global float *output, 
            read_only image2d_t input, 
            constant int *mask,
            private int maskSizeH)
{
    const int2 pos = (int2) (get_global_id (0), get_global_id (1));

    int count = 0;
    float f;
    float mean = 0.0;
    float std = 0.0;

    for (int a = -maskSizeH; a < maskSizeH + 1; a++) {
        for (int b = -maskSizeH; b < maskSizeH + 1; b++) {
            if (mask[a+maskSizeH+(b+maskSizeH)*(maskSizeH*2+1)] == 1) {
                count++;
                mean += read_imagef(input, smp, pos + (int2)(a,b)).x;
            }
        }
    }

    mean /= count;

    for (int a = -maskSizeH; a < maskSizeH + 1; a++) {
        for (int b = -maskSizeH; b < maskSizeH + 1; b++) {
            if (mask[a+maskSizeH+(b+maskSizeH)*(maskSizeH*2+1)] == 1) {
                f = read_imagef(input, smp, pos + (int2)(a,b)).x;
                std += (f - mean) * (f - mean);
            }
        }
    }

    std = sqrt(std/count);
 
    f = read_imagef(input, smp, pos).x;
    output[pos.x + pos.y*get_global_size(0)] = exp((f - mean)/std);
}

