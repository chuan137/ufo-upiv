const sampler_t smp = CLK_NORMALIZED_COORDS_FALSE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_NEAREST;

kernel void
likelihood (global float *output, 
            read_only image3d_t input, 
            constant int *mask,
            int maskSizeH, 
            int mask_num_ones,
            int n,
            local float *local_mem)
{
    int shift = 6;

    unsigned glb_size_x = get_global_size(0);
    unsigned glb_size_y = get_global_size(1);

    unsigned loc_size_x = get_local_size(0);
    unsigned loc_size_y = get_local_size(1);
    unsigned loc_mem_size_x = loc_size_x + 2 * shift;
    
    unsigned glb_x = get_global_id(0);
    unsigned glb_y = get_global_id(1);
    const int4 glb_pos = (int4) (glb_x, glb_y, n, 0);
    
    unsigned loc_x = get_local_id(0);
    unsigned loc_y = get_local_id(1);
    unsigned local_tmp_id;

    local_tmp_id = (shift + loc_y) * loc_mem_size_x + (shift + loc_x);
    local_mem[local_tmp_id] = read_imagef(input, smp, glb_pos).x; 

    if (loc_x < shift) {
        local_tmp_id = (shift + loc_y) * loc_mem_size_x + loc_x;
        local_mem[local_tmp_id] = read_imagef(input, smp, (int4)(glb_x - shift, glb_y, n, 0)).x;
    }

    if (loc_y < shift) {
        local_tmp_id = loc_y * loc_mem_size_x + (shift + loc_x);
        local_mem[local_tmp_id] = read_imagef(input, smp, (int4)(glb_x, glb_y - shift, n, 0)).x;
    }

    if (loc_x + shift >= loc_size_x) {
        local_tmp_id = (loc_y + shift) * loc_mem_size_x + (loc_x + 2*shift);
        local_mem[local_tmp_id] = read_imagef(input, smp, (int4)(glb_x + shift, glb_y, n, 0)).x;
    }

    if (loc_y + shift >= loc_size_y) {
        local_tmp_id = (loc_y + 2*shift) * loc_mem_size_x + (loc_x + shift);
        local_mem[local_tmp_id] = read_imagef(input, smp, (int4)(glb_x, glb_y + shift, n, 0)).x;
    }

    if (loc_x < shift && loc_y < shift) {
        local_tmp_id = loc_y * loc_mem_size_x + loc_x;
        local_mem[local_tmp_id] = read_imagef(input, smp, (int4)(glb_x - shift, glb_y-shift, n, 0)).x;
    }

    if (loc_x + shift >= loc_size_x && loc_y < shift) {
        local_tmp_id = loc_y * loc_mem_size_x + (loc_x + 2*shift);
        local_mem[local_tmp_id] = read_imagef(input, smp, (int4)(glb_x + shift, glb_y - shift, n, 0)).x;
    }

    if (loc_x < shift && loc_y + shift >= loc_size_y) {
        local_tmp_id = (loc_y + 2*shift) * loc_mem_size_x + loc_x;
        local_mem[local_tmp_id] = read_imagef(input, smp, (int4)(glb_x - shift, glb_y + shift, n, 0)).x;
    }

    if (loc_x + shift >= loc_size_x && loc_y + shift >= loc_size_y) {
        local_tmp_id = (loc_y + 2*shift) * loc_mem_size_x + loc_x + 2*shift;
        local_mem[local_tmp_id] = read_imagef(input, smp, (int4)(glb_x + shift, glb_y + shift, n, 0)).x;
    }

    barrier(CLK_LOCAL_MEM_FENCE);

    float mean = 0.0f, std = 0.0f, f;

    for (int a = -maskSizeH; a < maskSizeH + 1; a++) {
        for (int b = -maskSizeH; b < maskSizeH + 1; b++) {
            local_tmp_id = (loc_y + shift + b) * loc_mem_size_x + (loc_x + shift +a);
            mean += local_mem[local_tmp_id] * mask[a+maskSizeH+(b+maskSizeH)*(maskSizeH*2+1)];
        }
    }
    mean = mean / mask_num_ones;

    for (int a = -maskSizeH; a < maskSizeH + 1; a++) {
        for (int b = -maskSizeH; b < maskSizeH + 1; b++) {
            local_tmp_id = (loc_y + shift + b) * loc_mem_size_x + (loc_x + shift +a);
            f = local_mem[local_tmp_id];
            std += (f - mean) * (f -mean) * mask[a+maskSizeH+(b+maskSizeH)*(maskSizeH*2+1)];
        }
    }
    std = sqrt(std / mask_num_ones);

    local_tmp_id = (loc_y + shift) * loc_mem_size_x + (loc_x + shift);
    f = local_mem[local_tmp_id];
    unsigned idx = glb_pos.x + glb_pos.y*get_global_size(0) + n*get_global_size(0)*get_global_size(1);
    output[idx] = exp((f - mean)/std);
}

