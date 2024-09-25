from tests.python.utils_test import log_test_wrapper


def test_multi_partition():
    """
    This test will attempt to create a multi-node, multi-partition Ray Cluster.  Multi-node means more than one node.  Multi-partition means hetergenous nodes (nodes have different hardware).  This requires setting up the head node, CPU nodes, and GPU nodes on different computing devices and aggregating them into a single Ray Cluster.

    After bringing up the multi-partition cluster, you will need to ssh into the head node and execute the multi_partition_script.sh to run the test.
    """

    # Setup head
    log_test_wrapper(
        "tests/scripts/multi_partition_head_test.sh",
        "logs/ray-mp-head-test.log",
        "Ray runtime started",
    )

    # Setup CPU workers
    log_test_wrapper(
        "tests/scripts/multi_partition_workers_cpu_test.sh",
        "logs/ray-mp-workers-cpu-test.log",
        "Ray runtime started",
    )

    # Setup GPU workers
    log_test_wrapper(
        "tests/scripts/multi_partition_workers_gpu_test.sh",
        "logs/ray-mp-workers-gpu-test.log",
        "Ray runtime started",
    )
