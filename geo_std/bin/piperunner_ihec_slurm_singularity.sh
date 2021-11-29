#!/bin/bash

jobFile=$1
BACKEND=$2
if [[ $# -eq 3 ]]; then 
  OUTDIR="-Dbackend.providers.$BACKEND.config.root=$3"
else
  OUTDIR=""
fi

CROMWELL_HOME="/home/frosig/scratch/test_pipeline/bin/cromwell-34.jar"
BACKEND_CONF="/scratch/frosig/chip-seq-ihec-test/singularity-wrapper-encode/integrative_analysis_chip/encode-wrapper/backend_ihec_slurm_singularity.conf"
WORKFLOW_OPT="/scratch/frosig/chip-seq-ihec-test/singularity-wrapper-encode/integrative_analysis_chip/encode-wrapper/v2/singularity_container.json"
CHIP="/scratch/frosig/chip-seq-ihec-test/singularity-wrapper-encode/integrative_analysis_chip/encode-wrapper/v2/chip.wdl"

java -jar -Dconfig.file=$BACKEND_CONF -Dbackend.default=$BACKEND $OUTDIR $CROMWELL_HOME run $CHIP -i $jobFile -o $WORKFLOW_OPT
echo "return:$?"
