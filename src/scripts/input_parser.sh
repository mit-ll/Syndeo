#!/bin/bash

# Defaults
export HEAD_NODE_ADDR="None"
export N_CPUS=1
export N_GPUS=0

function info {
    echo "-a=<str>      --address=<str>     # head IP address"
    echo "-c=<int>      --cpus=<int>        # cpus per worker"
    echo "-g=<int>      --gpus=<int>        # gpus per worker"
}

for i in "$@"
do
    case $i in
        -a=*|--address=*)
            HEAD_NODE_ADDR="${i#*=}"
            ;;

        -c=*|--cpus=*)
            N_CPUS="${i#*=}"
            ;;

        -g=*|--gpus=*)
            N_GPUS="${i#*=}"
            ;;

        --help)
            info
            exit 0
            ;;

        *)
            echo "Invalid option"        # unknown option
            ;;
    esac
done
