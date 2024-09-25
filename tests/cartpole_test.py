import os

from tests.python.utils_test import log_test_wrapper


def test_cartpole_cpu():
    """Runs the following steps:

    1. Allocate CPU nodes from SLURM.
    2. Setup Ray Cluster.
    3. Run Cartpole environment on Ray Cluster.
    """

    log_test_wrapper(
        "tests/scripts/cartpole_cpu_test.sh",
        "logs/slurm-cartpole-cpu-test.log",
        "Successully executed test!",
        timeout=300,
    )


def test_cartpole_gpu():
    """Runs the following steps:

    1. Allocate GPU nodes from SLURM.
    2. Setup Ray Cluster.
    3. Run Cartpole environment on Ray Cluster.
    """

    log_test_wrapper(
        "tests/scripts/cartpole_gpu_test.sh",
        "logs/slurm-cartpole-gpu-test.log",
        "Successully executed test!",
    )


def test_cartpole_container():
    """Perform the following steps:

    1. Allocate CPU nodes from SLURM.
    2. Copy container to SLURM nodes.
    3. Start Ray Cluster from containers.
    4. Run the Cartpole experiment.
    """

    # Verify that the Apptainer file exists
    assert os.path.isfile(
        "containers/test_container.sif"
    ), f"Container containers/test_container.sif not found!\n\
            1. Build containers/test_container.def on a system with root\n\
            2. Place the built test_container.sif in containers/test_container.sif\n\
            3. Rerun this test!"

    # Verify logs are correct
    log_test_wrapper(
        "tests/scripts/cartpole_container_test.sh",
        "logs/slurm-cartpole-container.log",
        "RLLib running of cartpole completed successfully!",
        timeout=300,
    )
