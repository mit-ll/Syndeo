from tests.python.utils_test import log_test_wrapper


def test_basic_cpu():
    """This script will:

    1. Allocate a few CPU nodes from SLURM.
    2. Setup a Ray Cluster.
    3. Print :code:`hello world`
    """

    log_test_wrapper(
        "tests/scripts/basic_cpu_test.sh",
        "logs/slurm-basic-cpu-test.log",
        "Successully executed test!",
    )


def test_basic_gpu():
    """This script will:

    1. Allocate a few GPU nodes from SLURM.
    2. Setup a Ray Cluster.
    3. Print :code:`hello world`
    """

    log_test_wrapper(
        "tests/scripts/basic_gpu_test.sh",
        "logs/slurm-basic-gpu-test.log",
        "Successully executed test!",
    )
