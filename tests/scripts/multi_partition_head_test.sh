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
#SBATCH --job-name ray_mp_head
#SBATCH --output logs/ray-mp-head-test.log
#SBATCH --cpus-per-task=48
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --time 0-00:10:00
#SBATCH --partition=xeon-p8
#SBATCH --distribution=nopack

# Setup Ray head
# --export: export the head address info to a directory (default is ./tmp)
source src/scripts/setup_ray_head.sh --dir=$HOME/ray_tmp

sleep infinity
