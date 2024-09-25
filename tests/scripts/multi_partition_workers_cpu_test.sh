#!/bin/bash

#===================================================================================================
#
#         USAGE:  sbatch <file>.sh
#
#   DESCRIPTION:  Setup multi-node CPU Ray workers.
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
#SBATCH --job-name ray_mp_workers_cpu
#SBATCH --output logs/ray-mp-workers-cpu-test.log
#SBATCH --cpus-per-task=64
#SBATCH --nodes=4
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=1
#SBATCH --time 0-00:10:00
#SBATCH --partition=manycore
#SBATCH --distribution=nopack

# Setup Ray workers
# --gpus: GPUs per worker
# --dir: directory to import head info from
# --index: index to start node allocation (0 means all nodes)
source src/scripts/setup_ray_workers.sh --gpus=0 --dir=$HOME/ray_tmp --index=0

sleep infinity
