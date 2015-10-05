parms = dict(
    in_path     = 'data/sampleC', 
    out_file    = 'data/res.tif',
    width       = 1024,
    height      = 1024,
    number      = 1,
    start       = 0,
    scale       = 2,
    xshift      = 0,
    yshift      = 0,
    ring_thick  = 6,
    ring_start  = 4,
    ring_end    = 40,
    ring_step   = 2,
    ring_method = 0,
    likelihoodmask = 13,
    likelihoodmaskinner = 6,
    contrast_c1 = -0.5,
    contrast_c2 = 10,
    contrast_c3 = 4,
    contrast_c4 = 4,
    candi_threshold = 100,
    azimu_peak = 1.001
    )

config = dict (
    schedfixed = False,
    profiling = False,
    deviceCPU = False,
    graph = 0
    )
