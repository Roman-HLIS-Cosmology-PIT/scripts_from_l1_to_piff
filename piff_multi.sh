#!/bin/bash
#SBATCH --job-name=Piff_Array
#SBATCH --nodes=1
#SBATCH --cpus-per-task=18
#SBATCH --ntasks=1
#SBATCH --mem=32gb
#SBATCH --time=72:00:00
#SBATCH --output=logs/piff_%A_%a.log
#SBATCH --error=logs/piff_%A_%a.err
#SBATCH --account=pcon0003
#SBATCH --array=0-59%10


conda init bash
conda activate piff

ID_ARRAY=($(ls ffov_files/ffov_*.fits | grep -oE '[0-9]+'))

JOB_ID=${ID_ARRAY[$SLURM_ARRAY_TASK_ID]}

if [ -z "$JOB_ID" ]; then
    echo "No file found for Task ID $SLURM_ARRAY_TASK_ID. Exiting."
    exit 0
fi

# Explicitly ignore IDs 664 and 667
if [ "$JOB_ID" = "664" ] || [ "$JOB_ID" = "667" ]; then
    echo "ID ${JOB_ID} has already been processed. Skipping to avoid overwrite."
    exit 0
fi

echo "Processing file ID: ${JOB_ID} on Task ID: ${SLURM_ARRAY_TASK_ID}"

piffify piff_base.yaml \
    input.image_file_name=ffov_files/ffov_${JOB_ID}.fits \
    input.cat_file_name=true_star_cats/stars_${JOB_ID}.parquet \
    output.file_name=ffov_${JOB_ID}.piff \
    output.stats.0.file_name=hsm_${JOB_ID}.fits