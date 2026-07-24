import sys
from pyimcom.compress.compressutils import CompressedOutput
from pyimcom.config import Config
cfg = Config(sys.argv[1])
for i in range(1600):
    ibx = i%40
    iby = i//40
    fname = cfg.outstem + f'_{ibx:02d}_{iby:02d}.fits'
    fout = cfg.outstem + f'_{ibx:02d}_{iby:02d}.cpr.fits.gz'
    print(fname, '-->', fout); sys.stdout.flush()

    with CompressedOutput(fname) as f:
        for j in range(1,len(f.cfg.extrainput)):
            if (f.cfg.extrainput[j][:6].lower()=='gsstar' or f.cfg.extrainput[j][:5].lower()=='cstar'
                    or f.cfg.extrainput[j][:8].lower()=='gstrstar' or f.cfg.extrainput[j][:8].lower()=='gsfdstar'):
                f.compress_layer(j, scheme='I24B', pars={'VMIN': -1./64., 'VMAX': 7./64., 'BITKEEP': 20, 'DIFF': True, 'SOFTBIAS': -1})
            if f.cfg.extrainput[j][:5].lower()=='nstar':
                f.compress_layer(j, scheme='I24B', pars={'VMIN': -1500., 'VMAX': 10500., 'BITKEEP': 20, 'DIFF': True, 'SOFTBIAS': -1})
            if f.cfg.extrainput[j][:5].lower()=='gsext':
                f.compress_layer(j, scheme='I24B', pars={'VMIN': -1./64., 'VMAX': 7./64., 'BITKEEP': 20, 'DIFF': True, 'SOFTBIAS': -1})
            if f.cfg.extrainput[j][:10].lower()=='whitenoise':
                f.compress_layer(j, scheme='I24B', pars={'VMIN': -8, 'VMAX': 8, 'BITKEEP': 14, 'DIFF': True, 'SOFTBIAS': -1})
            if f.cfg.extrainput[j][:7].lower()=='1fnoise':
                f.compress_layer(j, scheme='I24B', pars={'VMIN': -32, 'VMAX': 32, 'BITKEEP': 14, 'DIFF': True, 'SOFTBIAS': -1})
            if f.cfg.extrainput[j][:6].lower()=='noise,':
                f.compress_layer(j, scheme='I24B', pars={'VMIN': -0.125, 'VMAX': 0.125, 'BITKEEP': 14, 'DIFF': True, 'SOFTBIAS': -1})
        f.to_file(fout, overwrite=True)
