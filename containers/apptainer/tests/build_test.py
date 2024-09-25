import pathlib
import subprocess

import pytest

from containers.apptainer.utils import verify_root


def test_build():
    """Attempts to build a basic Apptainer container with miniconda package manager.  This can only be done on a computer where the user has **root** access.  Otherwise, it will fail.

    Raises:
        Exception: Throws an error if any of the builds fail.
    """

    if verify_root() is False:
        pytest.skip("You need to have root privileges to execute this test.")

    # Create the output directory
    pathlib.Path("save").mkdir(parents=True, exist_ok=True)

    # Setup build arguments
    build_args1 = [
        "singularity",
        "build",
        "save/miniconda.sif",
        "containers/apptainer/templates/miniconda.def",
        "--force",
    ]
    build_args2 = [
        "singularity",
        "build",
        "save/base.sif",
        "containers/apptainer/templates/base.def",
        "--force",
    ]

    build_args = [build_args1, build_args2]

    # Run the sbatch script and capture output
    results = []

    for build_arg in build_args:
        result = subprocess.run(
            build_arg,
            capture_output=True,
            text=True,
            check=False,
        )
        results.append(result)

    # Check for error when sent to scheduler
    for result in results:
        if result.returncode != 0:
            raise RuntimeError(f"Invalid result: { result.returncode }, Error: {result}")
