#!/bin/bash

#===================================================================================================
#
#         USAGE:  sbatch <file>.sh
#
#   DESCRIPTION:  Gets IP addresses on multi-node GPU cluster.
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
#SBATCH --job-name test_ip_gpu
#SBATCH --output logs/slurm-ip-gpu-test.log
#SBATCH --cpus-per-task=40
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --time 0-00:05:00
#SBATCH --partition=gaia
#SBATCH --gres=gpu:volta:2
#SBATCH --distribution=nopack

# User Config
# --------------------------------------------------------------------------------------------------
source src/scripts/setup_ray_head.sh
source src/scripts/setup_ray_workers.sh --gpus=1 --index=1

# Verification
# --------------------------------------------------------------------------------------------------
# Provides verification of Ray runtimes.
# Argument 1: Slurm log file.
# Argument 2: Number of nodes to check for.
python src/validation/nodes.py "logs/slurm-ip-gpu-test.log" 2

# Python Code
# --------------------------------------------------------------------------------------------------
# -u     : unbuffered binary stdout and stderr
python -u tests/python/ip_test.py $HEAD_NODE_ADDR

# Cleanup
# --------------------------------------------------------------------------------------------------
source src/scripts/shutdown_ray.sh
