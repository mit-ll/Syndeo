##########
Benchmarks
##########

These are benchmarks were generated using Syndeo with containerized Ray on the MIT LLSC architecture.  Each experiment measures throughput of Mujoco environments under different node configurations.  Results indicate that as nodes are added, the throughput increases.


.. raw:: html
    :class: full-width

    <iframe src="../_static/benchmarks/bar.html" height="500px" width="100%"></iframe>

.. raw:: html
    :class: full-width

    <iframe src="../_static/benchmarks/performance-line-0.html" height="1300px" width="100%"></iframe>

.. raw:: html
    :class: full-width

    <iframe src="../_static/benchmarks/performance-line-4.html" height="1000px" width="100%"></iframe>

#################
Mujoco Benchmarks
#################

Here is an end-to-end example of how to reproduce the Mujoco results from the paper.

1. Begin by cloning the repos to a development machine.  Build the container and copy it to your SLURM host.

.. code-block:: console

    # Clone the example repo
    git clone https://github.com/mit-ll/RL-Benchmarks.git

    # Build the containers
    cd RL-Benchmarks/containers
    sudo su -
    bash build.sh

    # Copy container to SLURM host
    scp rl_benchmarks.sif <SLURM_HOST>:containers/


1.  provides two example Syndeo scripts for running experiments:

* `Speed Test <https://github.com/mit-ll/RL-Benchmarks/blob/main/tests/syndeo-node-4-test-speed.py>`_
* `Train Test <https://github.com/mit-ll/RL-Benchmarks/blob/main/tests/syndeo-node-4-test-train.py>`_

.. note::
    :class: margin

    This experiment will setup four nodes on SLURM and deploy a Ray Cluster to run `RL Benchmarks <https://github.com/mit-ll/RL-Benchmarks.git>`_.  You will need to make modifications to the example script where it has :code:`TODO:` in the comments.

**RL_Benchmarks/tests/syndeo-node-4-test-speed.py**

.. code-block:: bash
    :emphasize-lines: 6, 11, 18, 20

    ...

    #SBATCH --exclusive
    #SBATCH --job-name rl_benchmarks_speed
    #SBATCH --output logs/rl_benchmarks-gaia-node-4-%j.log
    #SBATCH --cpus-per-task=40          # TODO: match with CPUs per node!!!
    #SBATCH --nodes=4
    #SBATCH --ntasks=4
    #SBATCH --ntasks-per-node=1
    #SBATCH --time 0-02:00:00
    #SBATCH --partition=gaia            # TODO: rename to your partition
    #SBATCH --distribution=nopack

    ##########################################################################################
    # User Config
    ##########################################################################################
    # Host Config
    HOST_WORKING_DIR="/state/partition1/user/$USER"     # TODO: must match node's local partition (hard disk)
    HOST_RAY_TMPDIR="$HOST_WORKING_DIR/tmp"
    HOST_SAVE="~/projects/rl_benchmarks/save/speed"     # TODO: modify to your save output directory

    ...

1. On the SLURM host clone the `Syndeo <https://github.com/mit-ll/Syndeo.git>`_ repo.  Copy your modified script into the Syndeo repo and execute the following commands.

.. code-block:: console

    ssh <SLURM_HOST>
    git clone https://github.com/mit-ll/Syndeo.git
    sbatch syndeo-node-4-test-speed.sh # this is your modified script


* You will see logs being generated in :code:`logs/*`.
* You can even use `Tensorboard <https://www.tensorflow.org/tensorboard/get_started>`_ to view the results located in the :code:`HOST_SAVE` directory.

Syndeo will take care of copying your container to all SLURM allocated nodes, starting up a Ray Cluster, and executing your python script on the head node.  All results will be saved to the output directory you have specified.
