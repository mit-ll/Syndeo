# 🧪 Integration Pytests

Each of the pytests included in this directory are designed to exercise a different part of the Ray + SLURM + Singularity pipeline.  Unfortunately, passing statements in the pytest logs are not sufficient for determining whether the test was successful.  In order to verify that the program is performing what you expect you will need to review the logs.

## Usage
```console
pytest tests/<*_test.py>::<test_*>      # This follows the convention of path:function
```

## Info
The types of tests that are included span:

| Scripts                  | Description                                                |
| ------------------------ | ---------------------------------------------------------- |
| basic_test.py            | Prints out hello world.                                    |
| ip_test.sh               | Prints out IP nodes.                                       |
| cartpole_test.py         | Runs RLLib's cartpole training.                            |
| cli_test.py              | Tests the CLI menu.                                        |
| multi_partition_tests.py | Tests multi-partition nodes.                               |
| utils_test.py            | Common utils for logging information and generating stats. |
