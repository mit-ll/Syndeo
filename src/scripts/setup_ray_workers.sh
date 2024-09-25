#!/bin/bash

#===================================================================================================
#
#         USAGE:  Should be sourced from a SLURM sbatch script.
#
#   DESCRIPTION:  Setup the Ray workers for a SLURM HPC system.
#
#       OPTIONS:  --tmpdir:             a temporary directory to write files to (host system)
#                 --gpus:               GPUs per worker to allocate
#                 --dir:                directory for reading head's IP address
#                 --index:              used to determine where worker indexing should start,
#                                       (index=0 for all nodes) or (index=1 to remove first node)
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
IMPORT_DIR="$HOME/tmp"                          # defaults to ~/tmp
IMPORT_INFO=0                                   # 0=<no import head IP>,    1=<import head IP>
CONTAINER_SETUP=0                               # 0=<no container>,         1=<container>
CONTAINER_SYNC=0                                # 0=<no sync>,              1=<sync>
CONTAINER_TGT_PATH="/tmp/ray_container.sif"     # target path to copy container to
N_GPU_PER_WORKER=0                              # number of GPUs to assign per worker
START_IDX=0                     # start index of nodes to allocate to worker from Slurm
FINAL_IDX=(${SLURM_NTASKS})     # final index of nodes to allocate to worker from Slurm
TMPDIR="/tmp"
RAY_TMPDIR="/tmp"

function info {
cat <<BANNER
setup_ray_workers.sh:
    -td     --tmpdir            # temporary directory for writing Ray cluster files
    -g      --gpus              # GPUs per worker
    -d      --dir               # Import directory for reading head IP info.
    -i      --index             # Indexing (index=0 for all nodes) | (index=1 to remove first node)
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

        -g=*|--gpus=*)
            N_GPU_PER_WORKER="${i#*=}"
            ;;

        -d=*|--dir=*)
            IMPORT_DIR="${i#*=}"
            IMPORT_INFO=1
            ;;

        -i=*|--index=*)
            START_IDX="${i#*=}"
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

# Import head node information
# Note: This is only needed for multi-partition SLURM configurations where the worker nodes need to read the address of the head node and connect to it.
# --------------------------------------------------------------------------------------------------
if [ $IMPORT_INFO = 1 ]; then
HEAD_NODE_ADDR=$(<$IMPORT_DIR/ray_head_node_addr.txt)
cat <<BANNER
----------------------------------------------------------------------------------------------
                            Ray Workers - Importing Ray Head Info
----------------------------------------------------------------------------------------------
HEAD_NODE_PATH          = $IMPORT_DIR/ray_head_node_addr.txt
HEAD_NODE_ADDR          = ${HEAD_NODE_ADDR}
BANNER
fi

cat <<BANNER
----------------------------------------------------------------------------------------------
                            Ray Workers - Starting Ray Nodes
----------------------------------------------------------------------------------------------
WORKER GPU per Node     = ${N_GPU_PER_WORKER}
WORKER Node TMPDIR      = ${TMPDIR}

Generating Directory: ${TMPDIR} across all nodes...
BANNER

NODES=$(scontrol show hostnames "$SLURM_JOB_NODELIST")
NODES_ARRAY=($NODES)
for ((  i=$START_IDX; i<$FINAL_IDX; i++ ))
do
    # Get the worker ID
    worker_node_id=${NODES_ARRAY[$i]}

    # Perform operations on each worker ID
    # worker_node_ip=$(srun --nodes=1 --ntasks=1 -w "$worker_node_id" hostname --ip-address)
    srun --nodes=1 --ntasks=1 -w "$worker_node_id" mkdir -p ${TMPDIR} &
    echo "WORKER Node ID $i       = $worker_node_id"
done

sleep 5s

# TODO: Determine whether the head node needs to be excluded
let "WORKER_N_NODES=(${SLURM_NTASKS} - ${START_IDX})"

if [ $CONTAINER_SYNC = 1 ]; then
cat <<BANNER
----------------------------------------------------------------------------------------------
                            Ray Workers - Syncing Container
----------------------------------------------------------------------------------------------
CONTAINER_SRC_PATH      = ${CONTAINER_SRC_PATH}
CONTAINER_TGT_PATH      = ${CONTAINER_TGT_PATH}
NODE_CONTAINER_DIR      = ${CONTAINER_TGT_PATH%/*}
Copying $CONTAINER_SRC_PATH -> $CONTAINER_TGT_PATH...
BANNER
    # Make container target directories if they do not exist
    echo " ----------------------[ Creating Directories for Each Container ]-----------------------"
    srun --nodes=${WORKER_N_NODES} --ntasks=${WORKER_N_NODES} --exclude=$HEAD_NODE_ID \
        mkdir -p ${CONTAINER_TGT_PATH%/*} &
    sleep 5s
    echo " ---------------------------------[ Copying Containers ]---------------------------------"
    srun \
        --nodes=${WORKER_N_NODES} \
        --ntasks=${WORKER_N_NODES} \
        --cpus-per-task=1 \
        --exclude=$HEAD_NODE_ID \
        cp -rf $CONTAINER_SRC_PATH $CONTAINER_TGT_PATH
    # sbcast --force $CONTAINER_SRC_PATH $CONTAINER_TGT_PATH
fi

# Start Ray workers
# --------------------------------------------------------------------------------------------------
# Description: Here we need to create one or more workers to be used by the scheduler.
#
# srun
#   --nodes: Request that a minimum of minnodes nodes be allocated to this job.
#   --ntasks: Specify the number of tasks to run. Note that the --cpus-per-task option will change this default.
#   --cpus-per-task: Request that ncpus be allocated per process. This may be useful if the job is multithreaded and requires more than one CPU per task for optimal performance.
#   --exclude: Request that a specific list of hosts not be included in the resources allocated to this job.
#
# ray start
#   -v: verbose
#   --address: the address to use for Ray
#   --block: provide this argument to block forever in this command
#   --num-cpus: the number of CPUs on this node
#   --num-gpus: the number of GPUs on this node
#   --temp-dir: manually specify the root temporary dir of the Ray process, only works when –head is specified
#
# References:
#   https://slurm.schedmd.com/srun.html
#   https://docs.ray.io/en/latest/cluster/cli.html#ray-start

if [ $CONTAINER_SETUP = 1 ]; then
cat <<BANNER
----------------------------------------------------------------------------------------------
                            Ray Workers - Running Container
----------------------------------------------------------------------------------------------
BANNER

    # Run with container
    srun \
        --nodes=${WORKER_N_NODES} \
        --ntasks=${WORKER_N_NODES} \
        --cpus-per-task=${SLURM_CPUS_PER_TASK} \
        --exclude=$HEAD_NODE_ID \
        --export=ALL,TMPDIR=${TMPDIR},RAY_TMPDIR=${RAY_TMPDIR} \
    singularity exec \
        --tmp-sandbox \
        --userns \
        --nv \
        --writable \
        $CONTAINER_TGT_PATH \
            ray start \
                -v \
                --address $HEAD_NODE_ADDR \
                --block \
                --num-cpus ${SLURM_CPUS_PER_TASK} \
                --num-gpus ${N_GPU_PER_WORKER} &
else
cat <<BANNER
----------------------------------------------------------------------------------------------
                            Ray Workers - Running Bare Metal
----------------------------------------------------------------------------------------------
BANNER

    # Run on host system
    srun \
        --nodes=${WORKER_N_NODES} \
        --ntasks=${WORKER_N_NODES} \
        --cpus-per-task=${SLURM_CPUS_PER_TASK} \
        --exclude=$HEAD_NODE_ID \
        --export=ALL,TMPDIR=${TMPDIR},RAY_TMPDIR=${RAY_TMPDIR} \
    ray start \
        -v \
        --address $HEAD_NODE_ADDR \
        --block \
        --num-cpus ${SLURM_CPUS_PER_TASK} \
        --num-gpus ${N_GPU_PER_WORKER} &
fi

sleep 10s
