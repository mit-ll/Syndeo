#!/bin/bash

#===================================================================================================
#
#         USAGE:  1) Setup a Ray Cluster from anywhere
#                 2) Activate your conda environment on the head node
#                 2) Run this script!
#
#       EXAMPLE:
#                 # Setup the Ray Cluster (can be done in Slurm shared file system)
#                 > pytest test/multi_partition_test.py
#
#                 # Execute your Python run script
#                 > ssh <head_ip_node_address>                      # can be found in the logs
#                 > conda activate <my_env>
#                 > bash test/scripts/multi_partition_script.sh     # Execute test script
#
#   DESCRIPTION:  Run a python script using the IP address of a Ray head cluster.
#                   * Assumes you are ssh into either the head node or one of the worker nodes
#                   * Assumes the Ray cluster is already up but not running
#                   * Assumes that the Ray head's <ip_address:port> info is located in the
#                     `/tmp/ray_head_node_addr.txt` file.
#
#        AUTHOR:  William Li, william.li@ll.mit.edu
#       COMPANY:  MIT Lincoln Laboratory
#       VERSION:  1.0
#       CREATED:  08/07/2023
#===================================================================================================

# Read in variables
export HEAD_NODE_ADDR=$(<${HOME}/ray_tmp/ray_head_node_addr.txt)

# Run the Python script
cat <<BANNER
--------------------------------------------------------------------------------------------------
                                  Starting Python Script"
--------------------------------------------------------------------------------------------------
HEAD_NODE_ADDR = $HEAD_NODE_ADDR
BANNER

# Run Python
python -u tests/python/cartpole_test.py ${HEAD_NODE_ADDR}

# Shutdown
source src/scripts/shutdown_ray.sh
