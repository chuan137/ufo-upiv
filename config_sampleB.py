parms = dict(
    in_path     = 'data/sampleB', 
    out_file    = 'data/res.tif',
    width       = 1024,
    height      = 1024,
    number      = 1,
    start       = 2,
    scale       = 2,
    xshift      = 0,
    yshift      = 0,
    ring_thick  = 6,
    ring_start  = 4,
    ring_end    = 80,
    ring_step   = 2,
    ring_method = 2,
    likelihoodmask = 13,
    likelihoodmaskinner = 6,
    contrast_c1 = 1,
    contrast_c2 = 8,
    contrast_c3 = 4,
    contrast_c4 = 6,
    candi_threshold = 200,
    azimu_peak = 1.0001
    )

config = dict (
    schedfixed = False,
    profiling = False,
    deviceCPU = False,
    graph = 0
    )