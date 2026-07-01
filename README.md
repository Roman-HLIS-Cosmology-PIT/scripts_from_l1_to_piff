# scripts_from_l1_to_piff
Scripts used in Nihar's run from raw OpenUniverse Images to L2 and piff files. This is currently optimized for OSC, and assumes paths on OSC. Please contact me if you would like to try doing this on your local machine. 

You will need to install romanimpreprocess, roman-hlis-l2-driver, and piff - I'll add a requirements.txt file at some point. 

Start with images taken from the OpenUniverse 2024 runs by running the `OpenUniverse_to_L1L2_Jun26.job` script. Make sure to change the input/output directories as needed, as well as the random seed. 
This calls the `OpenUniverse_to_L1L2_Jun26.py` script under the hood that was written by Chris Hirata. (I've also included a perl script that Chris wrote to make sure that all the necessary files have been copied over correctly - we ran this on a subset on OSC.)

Once that is done, you can run `ffov_maker.py` to make the full-field of view images from the L2 images that romanimpreprocess made. 

Now that the ffov files have been made, you can start running piff. But you need a star catalog for Piff! The script `process_catalogs.py` will pull those from s3 for you.

The config I ran piff with is saved in `piff_base.yaml`. To run on a single exposure, look at `piff.sh` and to run in parallel with a job array, look at `piff_multi.sh`. 

The last step was to convert to pyImcom readable legendre format, which is achieved by `convert_piff.py` and `convert_piff.sh`.

Happy processing! Contact me if there are questions!
