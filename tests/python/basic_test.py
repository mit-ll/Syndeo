import time
from collections import Counter

import ray
import typer
from utils_test import ray_stats


@ray.remote
def hello_world():
    """Prints `hello world` to the terminal."""

    time.sleep(0.001)
    return "hello world!"


def main(address: str):
    context = ray.init(address=address)
    ray_stats(context)

    print("-" * 100)
    print("Python Script".center(100))
    print("-" * 100)

    try:
        # retrieve the IP addresses
        futures = [hello_world.remote() for _ in range(100)]
        results = ray.get(futures)

        # logging
        print("Tasks executed")
        for text, num_tasks in Counter(results).items():
            print("    {} tasks on {}".format(num_tasks, text))

        print("Successully executed test!")
    finally:
        ray.shutdown()


if __name__ == "__main__":
    typer.run(main)
