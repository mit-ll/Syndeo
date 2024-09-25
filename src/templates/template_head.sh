#!/bin/bash

#===================================================================================================
#
#         USAGE:  sbatch <file>.sh
#
#   DESCRIPTION:  Setup a multi-node, multi-partition Ray head.
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

# Local variable initialization
HOSTENV={HOSTENV}

# Setup Ray head
# --dir: directory to export the head's IP information to
# --container: path to container that holds the environment code to use

case $HOSTENV in
    "container")
        # Singualrity Config
        export SINGULARITY_TMPDIR={TMPDIR}    # directory used by Apptainer/Singularity

        # Setup Ray Head
        source src/scripts/setup_ray_head.sh \
            --tmpdir={TMPDIR} \
            --dir={RAY_IP_DIR} \
            --container_src={CONTAINER_SRC_PATH} \
            --container_tgt={CONTAINER_TGT_PATH} \
            ;;

    "bare_metal")
        source src/scripts/setup_ray_head.sh \
            --tmpdir={TMPDIR} \
            --dir={RAY_IP_DIR}
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
