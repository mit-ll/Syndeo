import os
from pathlib import Path

from tests.python.utils_test import log_test_wrapper


def test_ip_cpu():
    """Runs the following steps:

    1. Allocate CPU nodes from SLURM.
    2. Setup Ray Cluster.
    3. Get IP from each node on Ray Cluster.
    """

    log_test_wrapper(
        "tests/scripts/ip_cpu_test.sh",
        "logs/slurm-ip-cpu-test.log",
        "Successully executed test!",
    )


def test_ip_gpu():
    """Runs the following steps:

    1. Allocate GPU nodes from SLURM.
    2. Setup Ray Cluster.
    3. Get IP from each node on Ray Cluster.
    """

    log_test_wrapper(
        "tests/scripts/ip_gpu_test.sh",
        "logs/slurm-ip-gpu-test.log",
        "Successully executed test!",
    )


def test_ip_container():
    """Perform the following steps:

    1. Allocate CPU nodes from SLURM.
    2. Copy container to SLURM nodes.
    3. Start Ray Cluster from containers.
    4. Get IP from each node on Ray Cluster.
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
        "tests/scripts/ip_container_test.sh",
        "logs/slurm-ip-container-test.log",
        "Successully executed test!",
    )
