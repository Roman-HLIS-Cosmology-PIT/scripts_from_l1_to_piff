#!/bin/bash
#SBATCH --job-name Piff
#SBATCH --nodes=1
#SBATCH --cpus-per-task=18
#SBATCH --ntasks=1
#SBATCH --mem=32gb
#SBATCH --time=72:00:00
#SBATCH --output=piff_try_nihar_v4.log
#SBATCH --error=piff_try_nihar_v4.err
#SBATCH --account=pcon0003

conda init bash

conda activate piff

piffify piff_base.yaml input.image_file_name=ffov_files/ffov_885.fits input.cat_file_name=true_star_cats/stars_885.parquet output.file_name=ffov_885.piff output.stats.0.file_name=hsm_885.fits

