parms = dict(
    in_path     = 'data/SampleA', 
    out_file    = 'data/res.tif',
    width       = 1024,
    height      = 1024,
    number      = 1,
    start       = 0,
    scale       = 2,
    xshift      = 0,
    yshift      = 0,
    ring_start  = 6,
    ring_end    = 120,
    ring_step   = 2,
    ring_method = 0,
    ring_thickness = 8,
    likelihoodmask = 13,
    likelihoodmaskinner = 8,
    contrast_c1 = 1,
    contrast_c2 = 6,
    contrast_gamma = 1.0,
    candi_threshold = 100,
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
