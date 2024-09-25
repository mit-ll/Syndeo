#!/bin/bash

#===================================================================================================
#
#         USAGE:  sbatch <file>.sh
#
#   DESCRIPTION:  Setup multi-node GPU Ray workers.
#
#       OPTIONS:  --exclusive:          sets hardware to be exclusive to this job
#                 --job-name:           name of the job
#                 --output:             output file name
#                 --cpus-per-task:      number of cpus set per task
#                 --nodes:              number of nodes to assign to this job
#                 --ntasks:             number of parallel tasks allowed (should match --nodes)
#                 --ntasks-per-node:    number of tasks to assign per node
#                 --time:               maximum time before killing job "days-hours:min:secs"
#                 --constraint:         type of hardware to use
#                 --partition:          type of partition used
#                 --gres:               gpu resource request
#
#        AUTHOR:  William Li, william.li@ll.mit.edu
#       COMPANY:  MIT Lincoln Laboratory
#       VERSION:  1.0
#       CREATED:  08/07/2023
#===================================================================================================

#SBATCH --exclusive
#SBATCH --job-name {JOB_NAME}
#SBATCH --output logs/{OUTPUT}.log
#SBATCH --cpus-per-task={CPUS_PER_TASK}
#SBATCH --nodes={NODES}
#SBATCH --ntasks={NODES}
#SBATCH --ntasks-per-node=1
#SBATCH --time {TIME}
#SBATCH --partition={PARTITION}
#SBATCH --gres={GRES}

# Local variable initialization
export HOSTENV={HOSTENV}

# Setup Ray head
# --tmpdir            # temporary directory to write files to (host system)
# --gpus              # GPUs per worker
# --dir:              # directory to import head info from
# --index:            # index to start node allocation (0 means all nodes)
# --container_src     # specify path to a source container to use
# --container_tgt     # location to copy container onto target file system

case $HOSTENV in
    "container")
        # Singualrity Config
        export SINGULARITY_TMPDIR={TMPDIR}    # directory used by Apptainer/Singularity

        # Setup Ray Workers (GPU)
        source src/scripts/setup_ray_workers.sh \
            --tmpdir={TMPDIR} \
            --gpus=2 \
            --dir={RAY_IP_DIR} \
            --index=0 \
            --container_src={CONTAINER_SRC_PATH} \
            --container_tgt={CONTAINER_TGT_PATH} \
            ;;

    "bare_metal")
        source src/scripts/setup_ray_workers.sh \
            --tmpdir={TMPDIR} \
            --gpus=2 \
            --dir={RAY_IP_DIR} \
            --index=0
            ;;

    *)
        echo "ERROR: This Ray configuration setup is not available. Please choose a different one."
        ;;
esac

# Verification
# --------------------------------------------------------------------------------------------------
# Provides verification of Ray runtimes.
# Argument 1: Slurm log file.
# Argument 2: Number of nodes to check for.
python src/validation/nodes.py "logs/{OUTPUT}.log" {NODES}

sleep infinity
