#!/bin/bash

#===================================================================================================
#
#         USAGE:  Should be sourced from a SLURM sbatch script.
#
#   DESCRIPTION:  Shutdown the Ray Cluster.
#
#       OPTIONS:  --container:          path of container to use on the node's file system
#
#        AUTHOR:  William Li, william.li@ll.mit.edu
#       COMPANY:  MIT Lincoln Laboratory
#       VERSION:  1.0
#       CREATED:  12/07/2023
#===================================================================================================

# Input Parser
# --------------------------------------------------------------------------------------------------
CONTAINER_SETUP=0

function info {
    echo "-c      --container   # path of container to use on the node's file system"
}

for i in "$@"
do
    case $i in
        -c|--container)
            CONTAINER_SETUP=1
            ;;

        -h|--help)
            info
            exit 0
            ;;

        *)
            echo "Error: Invalid argument!"
            info
            exit 0
            ;;
    esac
done

cat <<BANNER
----------------------------------------------------------------------------------------------
                                Shutdown Ray
----------------------------------------------------------------------------------------------
BANNER

# Ray stop
# --------------------------------------------------------------------------------------------------
# Options:
# -f, --force: If set, ray will send SIGKILL instead of SIGTERM.
# -g, --grace-period <grace_period>: The time in seconds ray waits for processes to be properly
#
# References:
# https://docs.ray.io/en/latest/cluster/cli.html#ray-stop

export > logs/${SLURM_JOB_NAME}-${SLURM_JOB_ID}.txt

if [ $CONTAINER_SETUP = 1 ]; then
    singularity exec $CONTAINER_PATH ray stop --grace-period 30
else
    ray stop --grace-period 30
fi
