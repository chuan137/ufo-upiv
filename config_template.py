parms = dict(
    in_path     = 'data/Sample_0.tif',
    out_file    = 'res.tif',
    width       = 1024,
    height      = 1024,
    number      = 1,
    start       = 0,
    scale       = 2,
    xshift      = 0,
    yshift      = 0,
    ring_start  = 6,
    ring_end    = 40,
    ring_step   = 2,
    ring_method = 0,
    ring_thickness = 6,
    remove_high = 0,
    likelihoodmask = 13,
    likelihoodmaskinner = 8,
    contrast_c1 = 1,
    contrast_c2 = 20,
    contrast_gamma = 0.3,
    threads = 1,
    thld_azimu = 4,
    thld_likely = 40,
    )

config = dict (
    schedfixed = False,
    profiling = False,
    deviceCPU = True,
    graph = 'contrast'
    )
