#!/bin/bash
#SBATCH --time=1-00:00:00
#SBATCH --account=def-jacquesp
#SBATCH --cpus-per-task=1
#SBATCH --mem=5G
#SBATCH --job-name=Nextflow_master
#SBATCH --output=%x_%j.slurm

module load nextflow/20.04.1

nextflow run /home/frosig/nextflow/geo_std/IHEC_STD.nf -c /home/frosig/nextflow/geo_std/nextflow.config
