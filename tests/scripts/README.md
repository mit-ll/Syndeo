# 🧪 Bash Scripts

The scripts contained in this folder are designed to operate on the SLURM architecture.  The expected Command Line Interface (CLI) arguments are as follows:

```console
sbatch tests/scripts/<*_test.sh>  # replace with name of test you want to run
```

This will deploy the script to the SLURM scheduler which will then setup Ray and execute on the python program you have designated.

The types of tests that are included span:

| Scripts                        | Description                                        |
| ------------------------------ | -------------------------------------------------- |
| basic_cpu_test.sh              | Prints out hello world on each Ray CPU node.       |
| basic_cpu_test.sh              | Prints out hello world on each Ray GPU nodes.      |
| ip_container_test.sh           | Runs Ray on SLURM with Singularity containers.     |
| ip_cpu_test.sh                 | Prints out IP on each Ray CPU nodes.               |
| ip_gpu_test.sh                 | Prints out IP on each Ray GPU nodes.               |
| cartpole_container_test.sh     | Runs Ray on SLURM with Singularity containers.     |
| cartpole_cpu_test.sh           | Runs RLLib's Cartpole on Ray CPU nodes.            |
| cartpole_gpu_test.sh           | Runs RLLib's Cartpole on Ray GPU nodes.            |
| multi_partition_head.sh        | For setting up Ray multi-partition, execute first  |
| multi_partition_workers_cpu.sh | For setting up Ray multi-partition, execute second |
| multi_partition_workers_gpu.sh | For setting up Ray multi-partition, execute third  |
| multi_partition_script.sh      | For setting up Ray multi-partition, execute last   |

All of the test scripts can be run using the `sbatch` command, however the `multi_partition_*` scripts need to be executed in order because of how Ray registers nodes from SLURM with different partitions.
