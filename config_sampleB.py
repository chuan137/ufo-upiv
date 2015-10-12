parms = dict(
    in_path     = 'data/sampleB', 
    out_file    = 'data/res.tif',
    width       = 1024,
    height      = 1024,
    number      = 1,
    start       = 0,
    scale       = 2,
    xshift      = 0,
    yshift      = 0,
    ring_thick  = 10,
    ring_start  = 4,
    ring_end    = 60,
    ring_step   = 2,
    ring_method = 0,
    likelihoodmask = 13,
    likelihoodmaskinner = 4,
    contrast_c1 = 1,
    contrast_c2 = 8,
    contrast_c3 = 4,
    contrast_c4 = 6,
    candi_threshold = 150,
    azimu_peak = 1.0001
    )

config = dict (
    schedfixed = False,
    profiling = False,
    deviceCPU = False,
    graph = 0
    )
