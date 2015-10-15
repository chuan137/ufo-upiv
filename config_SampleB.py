parms = dict(
    in_path     = 'data/SampleB', 
    out_file    = 'data/res.tif',
    width       = 1024,
    height      = 1024,
    number      = 1,
    start       = 0,
    scale       = 2,
    xshift      = 0,
    yshift      = 0,
    ring_start  = 6,
    ring_end    = 80,
    ring_step   = 2,
    ring_method = 0,
    ring_thickness = 8,
    likelihoodmask = 13,
    likelihoodmaskinner = 8,
    contrast_c1 = 0,
    contrast_c2 = 10,
    contrast_gamma = 0.5,
    candi_threshold = 50,
    threads = 8,
    azimu_thld = 10,
    azimu_thld_likelihood = 300
    )

config = dict (
    schedfixed = False,
    profiling = False,
    deviceCPU = False,
    graph = 0
    )
