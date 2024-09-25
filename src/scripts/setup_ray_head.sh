#!/bin/bash

#===================================================================================================
#
#         USAGE:  Should be sourced from a SLURM sbatch script.
#
#   DESCRIPTION:  Setup the Ray head for a SLURM HPC system.
#
#       OPTIONS:  --tmpdir:             This is a special keyword that Ray looks for when setting
#                                       up Ray Clusters.  Temporary directory to write Ray files to
#                                       (default=~/tmp)
#                 --dir:                directory to export head's IP address, if setting up a
#                                       multi-partition Ray Cluster, this should be a shared
#                                       directory where all nodes can access (default=/tmp)
#                 --container_src:      source path of the container to use
#                 --container_tgt:      path of the file system to copy the container source for
#                                       the head node
#
#        AUTHOR:  William Li, william.li@ll.mit.edu
#       COMPANY:  MIT Lincoln Laboratory
#       VERSION:  1.0
#       CREATED:  12/07/2023
#===================================================================================================

# Input Parser
# --------------------------------------------------------------------------------------------------
CONTAINER_SETUP=0
CONTAINER_SYNC=0                                # 0=<no sync>,  1=<sync containers>
CONTAINER_TGT_PATH="/tmp/ray_container.sif"     # target path to copy container to
EXPORT_IP_DIR="$HOME/tmp"
TMPDIR="/tmp"                                   # should be same as RAY_TMPDIR
RAY_TMPDIR="/tmp"                               # should be same as RAY_TMPDIR

function info {
cat <<BANNER
setup_ray_head.sh:
    -td     --tmpdir            # temporary directory for writing Ray cluster files
    -d      --dir               # target directory for head IP info
    -cs     --container_src     # specify path to a source container to use
    -ct     --container_tgt     # location to copy container onto target file system
BANNER
}

for i in "$@"
do
    case $i in
        -td=*|--tmpdir=*)
            TMPDIR="${i#*=}"
            RAY_TMPDIR="${i#*=}"
            ;;

        -d=*|--dir=*)
            EXPORT_IP_DIR="${i#*=}"
            mkdir -p "$EXPORT_IP_DIR"
            ;;

        -cs=*|--container_src=*)
            CONTAINER_SRC_PATH="${i#*=}"
            CONTAINER_SYNC=1
            ;;

        -ct=*|--container_tgt=*)
            CONTAINER_TGT_PATH="${i#*=}"
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


# Initialization
# --------------------------------------------------------------------------------------------------
# Generate a list of node IP addresses for the nodes
NODES=$(scontrol show hostnames "$SLURM_JOB_NODELIST")
NODES_ARRAY=($NODES)

# Save the head node's IP address and port as environment variables
export HEAD_NODE_ID=${NODES_ARRAY[0]}
export HEAD_NODE_IP=$(srun --nodes=1 --ntasks=1 -w "$HEAD_NODE_ID" hostname --ip-address)
export HEAD_NODE_PORT=$(python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')
export HEAD_NODE_ADDR="$HEAD_NODE_IP:$HEAD_NODE_PORT"

# Export head node information
# Note: This is only needed for multi-partition SLURM setup.  The reason is because the head node's IP address needs to be placed in a location where all of the worker nodes can access and connect do.  The default /tmp will likely not work because it is only locally accessible.
echo "$HEAD_NODE_IP"   | tee $EXPORT_IP_DIR/ray_head_node_ip.txt
echo "$HEAD_NODE_ADDR" | tee $EXPORT_IP_DIR/ray_head_node_addr.txt

cat <<BANNER
----------------------------------------------------------------------------------------------
                                Ray Head - Exporting Head Info
----------------------------------------------------------------------------------------------
HEAD_NODE_IP PATH       = $EXPORT_IP_DIR/ray_head_node_ip.txt
HEAD_NODE_ADDR PATH     = $EXPORT_IP_DIR/ray_head_node_addr.txt

----------------------------------------------------------------------------------------------
                                Ray Head - Starting Node Setup
----------------------------------------------------------------------------------------------
Node IDs (ALL)          = $(scontrol show hostnames | tr '\n' ',')
HEAD Node ID            = ${HEAD_NODE_ID}
HEAD Node IP            = ${HEAD_NODE_IP}
HEAD Node Address       = ${HEAD_NODE_ADDR}
HEAD Node TMPDIR        = ${RAY_TMPDIR}
BANNER

# Make temporary directories if they do no exists (will hang unless you add & to command!)
# srun mkdir -p ${RAY_TMPDIR} &
srun --nodes=1 --ntasks=1 --nodelist=$NODES_ARRAY mkdir -p ${RAY_TMPDIR} &
sleep 5s    # wait for previous command to finish


if [ $CONTAINER_SYNC = 1 ]; then
cat <<BANNER
----------------------------------------------------------------------------------------------
                                Ray Head - Syncing Container
----------------------------------------------------------------------------------------------
CONTAINER_SRC_PATH      = ${CONTAINER_SRC_PATH}
CONTAINER_TGT_PATH      = ${CONTAINER_TGT_PATH}
Copying $CONTAINER_SRC_PATH -> $CONTAINER_TGT_PATH...
BANNER
    # Make container target directories if they do not exist
    echo " --------------------------------[ Creating a Directory ]--------------------------------"
    srun --nodes=1 --ntasks=1 --nodelist=$HEAD_NODE_ID mkdir -p ${CONTAINER_TGT_PATH%/*} &
    sleep 5s    # wait for previous command to finish
    echo " --------------------------------[ Copying a Container ]--------------------------------"
    srun --nodes=1 --ntasks=1 --nodelist=$HEAD_NODE_ID \
        cp -rf  $CONTAINER_SRC_PATH $CONTAINER_TGT_PATH
fi


# Start the head Ray server
# --------------------------------------------------------------------------------------------------
# Description: Here we need to start up the main server/scheduler which will be the driver for all jobs.  We have the option of running it from a container or directly on the host system.
#
# srun
#   --nodes: Request that a minimum of minnodes nodes be allocated to this job.
#   --ntasks: Specify the number of tasks to run. Note that the --cpus-per-task option will change this default.
#   --cpus-per-task: Request that ncpus be allocated per process. This may be useful if the job is multithreaded and requires more than one CPU per task for optimal performance.
#   --nodelist: Request a specific list of hosts. The job will contain all of these hosts and possibly additional hosts as needed to satisfy resource requirements.
#
# ray start
#   --verbose: verbose
#   --head: specifies a head node
#   --disable-usage-stats: disables sending information about your training to Ray engineering team
#   --block: provide this argument to block forever in this command
#   --dashboard-host: the host to bind the dashboard server to, either localhost (127.0.0.1) or 0.0.0.0 (available from all interfaces). By default, this is 127.0.0.1
#   --port: Port to forward. Use this multiple times to forward multiple ports.
#   --num-cpus: the number of CPUs on this node (should be 0 on head node to focus on scheduling!)
#   --num-gpus: the number of GPUs on this node (should be 0 on head node to focus on scheduling!)
#   --min-worker-port: minimum int for port (defaults to 10002)
#   --max-worker-port: maximum int for port (defaults to 19999)
#   --temp-dir: manually specify the root temporary dir of the Ray process, only works when –head is specified
#
# References:
#   https://slurm.schedmd.com/srun.html
#   https://docs.ray.io/en/latest/cluster/cli.html#ray-start

if [ $CONTAINER_SETUP = 1 ]; then
cat <<BANNER
----------------------------------------------------------------------------------------------
                                Ray Head - Running Container
----------------------------------------------------------------------------------------------
BANNER
    # Run with container
    srun \
        --nodes=1 \
        --ntasks=1 \
        --cpus-per-task=${SLURM_CPUS_PER_TASK} \
        --nodelist=$HEAD_NODE_ID \
        --export=ALL,TMPDIR=${TMPDIR},RAY_TMPDIR=${RAY_TMPDIR} \
    singularity exec \
        --tmp-sandbox \
        --userns \
        --nv \
        --writable \
        --bind $RAY_TMPDIR \
        $CONTAINER_TGT_PATH \
            ray start \
                --node-ip-address $HEAD_NODE_IP \
                --port $HEAD_NODE_PORT \
                --verbose \
                --head \
                --disable-usage-stats \
                --block \
                --dashboard-host 0.0.0.0 \
                --num-cpus 0 \
                --num-gpus 0 \
                --min-worker-port 10002 \
                --max-worker-port 19999 \
                --temp-dir $RAY_TMPDIR &
else
cat <<BANNER
----------------------------------------------------------------------------------------------
                                Ray Head - Running Bare Metal
----------------------------------------------------------------------------------------------
BANNER
    # Run on host system
    srun \
        --nodes=1 \
        --ntasks=1 \
        --cpus-per-task=${SLURM_CPUS_PER_TASK} \
        --nodelist=$HEAD_NODE_ID \
        --export=ALL,TMPDIR=${TMPDIR},RAY_TMPDIR=${RAY_TMPDIR} \
    ray start \
        --node-ip-address $HEAD_NODE_IP \
        --port $HEAD_NODE_PORT \
        --verbose \
        --head \
        --disable-usage-stats \
        --block \
        --dashboard-host 0.0.0.0 \
        --num-cpus 0 \
        --num-gpus 0 \
        --min-worker-port 10002 \
        --max-worker-port 19999 \
        --temp-dir $RAY_TMPDIR &
fi

sleep 5s
