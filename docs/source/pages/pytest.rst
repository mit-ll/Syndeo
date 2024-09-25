######
Pytest
######

Syndeo has examples of containerized workflows in its :code:`tests` directory.  However, it requires that you build the containers prior to executing the tests.

***********************
Building the Containers
***********************

Start by building a container on a development machine with sudo access.

.. code-block:: console

    ssh <DEV_MACHINE>

    # Clone Syndeo
    git clone https://github.com/mit-ll/Syndeo.git

    # Goto the container definition files
    cd syndeo/tests/containers

    # Build the containers
    sudo su -
    singularity build miniconda.sif miniconda.def   # parent container
    singularity build cartpole.sif cartpole_container.def   # child container

*****************
Setting up Syndeo
*****************

On the SLURM host clone the Syndeo repo:

.. code-block:: console

    # Clone Syndeo
    ssh <SLURM_HOST>
    git clone https://github.com/mit-ll/Syndeo.git

**************************
Moving Containers to SLURM
**************************

You must move the :code:`*.sif` container files from your development machine → SLURM host's container directory:

.. code-block:: console

    # Copy over container files
    ssh <DEV_MACHINE>

    cd syndeo/tests/containers
    scp cartpole_container.sif <SLURM_HOST>:syndeo/containers/

***********************
Modifying SLURM Scripts
***********************

Make modifications to :code:`tests/scripts/cartpole_container_test.sh` to match your SLURM settings.  A :code:`TODO` has been added to every line that needs user modifications.

**tests/scripts/cartpole_container_test.sh**

.. code-block:: bash
    :emphasize-lines: 4, 5, 10, 16

    ...
    #SBATCH --exclusive
    #SBATCH --job-name test_cartpole_container
    #SBATCH --output logs/slurm-cartpole-container.log      # TODO: name your log
    #SBATCH --cpus-per-task=28                              # TODO: set proper CPUs available to your node
    #SBATCH --nodes=3
    #SBATCH --ntasks=3
    #SBATCH --ntasks-per-node=1
    #SBATCH --time 0-00:05:00
    #SBATCH --partition=normal                              # TODO: ensure this is the correct name
    #SBATCH --distribution=nopack

    # Configs
    # --------------------------------------------------------------------------------------------------
    # Host Config
    HOST_WORKING_DIR="/state/partition1/user/$USER"         # TODO: set path to local partition (local node's hard disk)
    HOST_RAY_TMPDIR="$HOST_WORKING_DIR/tmp"

    # Singualrity Config
    export SINGULARITY_TMPDIR="$HOST_RAY_TMPDIR"

    # Container Config
    CONTAINER_SRC_PATH="containers/cartpole.sif"
    CONTAINER_TGT_PATH="$HOST_WORKING_DIR/ray_container.sif"
    ...

**********
Run Syndeo
**********

Finally run the tests.

.. note::
    :class: margin

    Pytest will exercise a containerized workflow for :code:`cartpole_test.py`.  You can do the same for :code:`ip_test.py` which also has a containerized workflow test.

.. code-block:: bash

    pytest tests/cartpole_test.py::test_cartpole_container

.. toctree::
    :maxdepth: 1

    pytest/index
