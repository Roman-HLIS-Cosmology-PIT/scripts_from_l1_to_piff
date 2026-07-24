import sys
import os
import numpy as np
from pyimcom.config import Config, Settings
from pyimcom.coadd import Block
from pyimcom.layer_wrapper import build_all_layers
from pyimcom.splitpsf.imsubtract_wrapper import run_imsubtract_all
from pyimcom.truthcats import gen_truthcats_from_cfg
if __name__=='__main__':
    cfg = Config(sys.argv[1])
    if len(sys.argv)==2:
        print(cfg.nblock)
        print(cfg.outstem)
        exit()
    if len(sys.argv)>3:
        if sys.argv[3]=='draw':
            build_all_layers(cfg, workers=12)
            exit()
        if sys.argv[3]=='imsubtract':
            run_imsubtract_all(sys.argv[1], workers=36, fft_workers=4, mmap=os.getenv('TMPDIR'))
            exit()
        if sys.argv[3]=='reduce':
            cfg.instamp_pad = 0.48 * Settings.arcsec
    cfg.tempfile = os.getenv('TMPDIR') + '/temp'
    cfg()
    print(cfg.to_file(None))
    block = Block(cfg=cfg, this_sub=int(sys.argv[2]))
    if int(sys.argv[2])==0: gen_truthcats_from_cfg(cfg)
