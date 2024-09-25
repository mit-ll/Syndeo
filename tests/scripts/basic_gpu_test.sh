#!/bin/bash

#===================================================================================================
#
#         USAGE:  sbatch <file>.sh
#
#   DESCRIPTION:  Basic test that connects multiple CPU nodes on SLURM and
#                 print "hello world".
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
#SBATCH --job-name test_basic_gpu
#SBATCH --output logs/slurm-basic-gpu-test.log
#SBATCH --cpus-per-task=40
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --constraint=xeon-g6
#SBATCH --partition=gaia
#SBATCH --distribution=nopack
#SBATCH --time 0-00:05:00
#SBATCH --gres=gpu:volta:1
#SBATCH --distribution=nopack

export TMPDIR=/state/partition1/user/$USER/raytemp
export RAY_TMPDIR=/state/partition1/user/$USER/raytemp
mkdir -p $TMPDIR

MASTER_HOST=$(hostname -s)
MASTER_PORT=$(python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')
export HEAD_NODE_ADDR="$MASTER_HOST:$MASTER_PORT"

srun \
     --nodes=1 \
     --ntasks=1 \
     --cpus-per-task=${SLURM_CPUS_PER_TASK} \
     --nodelist=$MASTER_HOST \
ray start \
     -v \
     --head \
     --block \
     --dashboard-host 0.0.0.0 \
     --port=$MASTER_PORT \
     --num-cpus ${SLURM_CPUS_PER_TASK} --temp-dir=$RAY_TMPDIR &


worker_num=$(($SLURM_NNODES-1))
srun \
     --nodes=${worker_num} \
     --ntasks=${worker_num} \
     --cpus-per-task=${SLURM_CPUS_PER_TASK} \
     --exclude=$MASTER_HOST \
ray start \
     -v \
     --address $HEAD_NODE_ADDR \
     --block \
     --num-cpus ${SLURM_CPUS_PER_TASK} &

# Verification
# --------------------------------------------------------------------------------------------------
# Provides verification of Ray runtimes.
# Argument 1: Slurm log file.
# Argument 2: Number of nodes to check for.
python src/validation/nodes.py "logs/slurm-basic-gpu-test.log" 2

python -u tests/python/basic_test.py $HEAD_NODE_ADDR

ray stop --force
