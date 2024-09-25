import os

from typer.testing import CliRunner

from main import app
from tests.python.utils_test import check_logs

runner = CliRunner()


def test_setup():
    """Runs the following steps:

    1. Verifies the `setup-head` CLI command does not error out.
    2. Verifies the `setup-cpu` CLI command does not error out.
    3. Verifies the `setup-gpu` CLI command does not error out.
    """

    result1 = runner.invoke(
        app, ["setup-head", "--partition", "xeon-p8", "--output", "cli_test_head"]
    )
    result2 = runner.invoke(app, ["setup-cpu", "--partition", "normal", "--output", "cli_test_cpu"])
    result3 = runner.invoke(app, ["setup-gpu", "--partition", "gaia", "--output", "cli_test_gpu"])

    assert result1.exit_code == 0
    assert result2.exit_code == 0
    assert result3.exit_code == 0

    assert "Success!" in result1.stdout
    assert "Success!" in result2.stdout
    assert "Success!" in result3.stdout


def test_show():
    """Verifies that the CLI `show` command does not error out."""

    runner.invoke(app, ["setup-head", "--partition", "xeon-p8", "--output", "cli_test_head"])
    runner.invoke(app, ["setup-cpu", "--partition", "normal", "--output", "cli_test_cpu"])
    runner.invoke(app, ["setup-gpu", "--partition", "gaia", "--output", "cli_test_gpu"])
    result = runner.invoke(app, ["show"])

    assert result.exit_code == 0


def test_run_bare_metal():
    """This test will use the CLI to create a Ray Cluster on SLURM bare-metal.  Runs the following steps:

    1. Cleanup any files from previous runs.
    2. Use the CLI command to setup a head node. (bare-metal)
    3. Use the CLI command to setup some CPU nodes. (bare-metal)
    4. Use the CLI command to setup some GPU nodes. (bare-metal)
    5. Use the CLI command to activate the Ray Cluster.
    6. Verify from the logs that all Ray runtimes successfully deploy!
    """

    # Delete old logs
    for file_path in [
        "logs/cli_head_bare_metal_test.log",
        "logs/cli_cpu_bare_metal_test.log",
        "logs/cli_gpu_bare_metal_test.log",
    ]:
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Start with clean slate
    runner.invoke(app, ["delete-all"])

    runner.invoke(
        app,
        [
            "setup-head",
            "--partition",
            "xeon-p8",
            "--output",
            "cli_head_bare_metal_test",
            "--tmpdir",
            "/state/partition1/user/$USER/tmp",
        ],
    )
    runner.invoke(
        app,
        [
            "setup-cpu",
            "--partition",
            "normal",
            "--output",
            "cli_cpu_bare_metal_test",
            "--tmpdir",
            "/state/partition1/user/$USER/tmp",
        ],
    )
    runner.invoke(
        app,
        [
            "setup-gpu",
            "--partition",
            "gaia",
            "--output",
            "cli_gpu_bare_metal_test",
            "--tmpdir",
            "/state/partition1/user/$USER/tmp",
        ],
    )
    runner.invoke(app, ["run"])

    check_logs("logs/cli_head_bare_metal_test.log", "Ray runtime started")
    check_logs("logs/cli_cpu_bare_metal_test.log", "Ray runtime started")
    check_logs("logs/cli_gpu_bare_metal_test.log", "Ray runtime started")


def test_run_container():
    """This test will use the CLI to create a Ray Cluster on SLURM with containers.  Runs the following steps:

    1. Cleanup any files from previous runs.
    2. Use the CLI command to setup a head node. (containerized)
    3. Use the CLI command to setup some CPU nodes. (containerized)
    4. Use the CLI command to setup some GPU nodes. (containerized)
    5. Use the CLI command to activate the Ray Cluster.
    6. Verify from the logs that all Ray runtimes successfully deploy!
    """

    # Delete old logs
    for file_path in [
        "logs/cli_head_container_test.log",
        "logs/cli_cpu_container_test.log",
        "logs/cli_gpu_container_test.log",
    ]:
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Start with clean slate
    runner.invoke(app, ["delete-all"])

    runner.invoke(
        app,
        [
            "setup-head",
            "--partition",
            "xeon-p8",
            "--output",
            "cli_head_container_test",
            "--hostenv",
            "container",
            "--tmpdir",
            "/state/partition1/user/$USER/tmp",
            "--container-src-path",
            "containers/test_container.sif",
            "--container-tgt-path",
            "/state/partition1/user/$USER/ray_container.sif",
        ],
    )
    runner.invoke(
        app,
        [
            "setup-cpu",
            "--partition",
            "normal",
            "--output",
            "cli_cpu_container_test",
            "--hostenv",
            "container",
            "--tmpdir",
            "/state/partition1/user/$USER/tmp",
            "--container-src-path",
            "containers/test_container.sif",
            "--container-tgt-path",
            "/state/partition1/user/$USER/ray_container.sif",
        ],
    )
    runner.invoke(
        app,
        [
            "setup-gpu",
            "--partition",
            "gaia",
            "--output",
            "cli_gpu_container_test",
            "--hostenv",
            "container",
            "--tmpdir",
            "/state/partition1/user/$USER/tmp",
            "--container-src-path",
            "containers/test_container.sif",
            "--container-tgt-path",
            "/state/partition1/user/$USER/ray_container.sif",
        ],
    )
    runner.invoke(app, ["run"])

    check_logs("logs/cli_head_container_test.log", "Ray runtime started", timeout=500)
    check_logs("logs/cli_cpu_container_test.log", "Ray runtime started", timeout=500)
    check_logs("logs/cli_gpu_container_test.log", "Ray runtime started", timeout=500)
