###############
Troubleshooting
###############

************
SLURM script
************

The :code:`--ntasks` must be less than or equal to :code:`--nodes` requested in SBATCH.

.. code-block:: bash

    # This will work
    #SBATCH --nodes=4
    #SBATCH --ntasks=4


Here is an example that will cause an error:

.. code-block:: bash

    # This will fail
    #SBATCH --nodes=4
    #SBATCH --ntasks=10


.. important::

    When creating a Ray Cluster be aware of what the physical resources on each compute device are.  You will only be able to allocate a maximum of physical resources from each compute type and node.  You can configure defaults by modifying the :code:`src/resources.json` file.

******************
Multiple Ray Users
******************

If there are multiple users trying to create Ray clusters then you will need to set different `ports to deconflict <https://docs.ray.io/en/latest/cluster/vms/user-guides/community/slurm.html>`_.  This is an issue that will need to be resolved before rolling out to multiple users.

**************
Setting TMPDIR
**************

Ray needs a :code:`TMPDIR` directory to write out its **Ray session files** to connect to the Ray Cluster.  The :code:`TMPDIR` need to meet two criteria:

1) :code:`TMPDIR` must be a writable location.
2) :code:`TMPDIR` must be mounted on the host system.

An issue with the Ray backend is that it uses :code:`TMPDIR` to set up its socket connections.  The problem is described `here <https://gitlab.com/outflow-project/outflow/-/issues/21>`__.

.. error::

    The error below is raised when using the backend: **ray**:

    .. code-block::

        `OSError: AF_UNIX path length cannot exceed 107 bytes`


    Ray needs to create a temporary folder. The path of this folder is composed of two parts:

    * Example of a part created by :code:`tempfile.mkdtemp(prefix="outflow_ray_")`:

    .. code-block::

        `/var/folders/qj/147cfvxs1xq6bp88xdcd4vt80000gq/T/outflow_ray_b2f2h7js`

    * Example of a part created with :code:`strftime` in :code:`ray/node.py` :

    .. code-block::

        `session_2021-05-05_16-16-18_112187_70483`


    Both are long, and there is a system limitation of **107 bytes** for sockets names.  See `issue <https://github.com/ray-project/ray/issues/7724>`_ where the problem is described

    A workaround is to set en environment variable :code:`TMPDIR`, :code:`TEMP` or :code:`TMP` to :code:`/tmp/` stated `here <https://docs.python.org/3/library/tempfile.html#tempfile.mkstemp>`__. :code:`Tempfile.mkdtemp`` will return a much shorter temporary file name.
