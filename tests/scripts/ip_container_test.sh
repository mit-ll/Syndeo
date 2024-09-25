#!/bin/bash

#===================================================================================================
#
#         USAGE:  sbatch <file>.sh
#
#   DESCRIPTION:  Gets IP addresses on multi-node CPU cluster.
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
#SBATCH --job-name test_ip_cpu
#SBATCH --output logs/slurm-ip-container-test.log
#SBATCH --cpus-per-task=28
#SBATCH --nodes=3
#SBATCH --ntasks=3
#SBATCH --ntasks-per-node=1
#SBATCH --time 0-00:05:00
#SBATCH --partition=xeon-p8
#SBATCH --distribution=nopack

# Configs
# --------------------------------------------------------------------------------------------------
# Host Config
HOST_WORKING_DIR="/state/partition1/user/$USER"
HOST_RAY_TMPDIR="$HOST_WORKING_DIR/tmp"

# Singualrity Config
export SINGULARITY_TMPDIR="$HOST_RAY_TMPDIR"

# Container Config
CONTAINER_SRC_PATH="containers/test_container.sif"
CONTAINER_TGT_PATH="$HOST_WORKING_DIR/ray_container.sif"

source src/scripts/setup_ray_head.sh \
    --tmpdir=$HOST_RAY_TMPDIR \
    --container_src=$CONTAINER_SRC_PATH \
    --container_tgt=$CONTAINER_TGT_PATH \

source src/scripts/setup_ray_workers.sh \
    --tmpdir=$HOST_RAY_TMPDIR \
    --gpus=1 \
    --index=1 \
    --container_src=$CONTAINER_SRC_PATH \
    --container_tgt=$CONTAINER_TGT_PATH

# Verification
# --------------------------------------------------------------------------------------------------
# Provides verification of Ray runtimes.
# Argument 1: Slurm log file.
# Argument 2: Number of nodes to check for.
python src/validation/nodes.py "logs/slurm-ip-container-test.log" 3

# Container Run
# --------------------------------------------------------------------------------------------------
# --no-home:            disable mounting the home directory
# --writable-tmpfs:     enable write access within container, but do not save on exit
# --bind:               bind host system paths to container paths
singularity exec \
    --tmp-sandbox \
    --userns \
    --writable \
    --bind $HOST_RAY_TMPDIR \
    $CONTAINER_TGT_PATH \
    python -u /domi/syndeo/tests/python/ip_test.py $HEAD_NODE_ADDR

# Cleanup
# --------------------------------------------------------------------------------------------------
source src/scripts/shutdown_ray.sh
