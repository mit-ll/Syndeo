import socket
import time
from collections import Counter

import ray
import typer
from utils_test import ray_stats


@ray.remote
def f() -> str:
    """Returns the IP address of the node.

    Returns:
        str: IP address of the node.
    """
    time.sleep(0.001)
    # Return IP address.
    return socket.gethostbyname(socket.gethostname())


def main(address: str):
    # ray start
    context = ray.init(address=address)
    ray_stats(context)

    print("-" * 100)
    print("Python Script".center(100))
    print("-" * 100)

    tic = time.time()

    try:
        # retrieve the IP addresses
        object_ids = [f.remote() for _ in range(10000)]
        ip_addresses = ray.get(object_ids)

        # calculate the time delta
        toc = time.time()
        time_delta = round(toc - tic, 1)

        # logging
        print("Tasks executed")
        for ip_address, num_tasks in Counter(ip_addresses).items():
            print("    {} tasks on {}".format(num_tasks, ip_address))

        print(f"Processing Time: {time_delta}secs")
        print("Successully executed test!")

    finally:
        ray.shutdown()


if __name__ == "__main__":
    typer.run(main)
