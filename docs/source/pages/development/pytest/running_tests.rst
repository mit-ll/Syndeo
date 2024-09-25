🧪 Running Tests
================
To execute the container tests you will first need to build the containers on a development system with root privileges and then transfer the built containers to SLURM:

.. code-block:: console

    cd tests/containers
    sudo su -

    singularity build cartpole.sif cartpole_container.def
    singularity build ip.sif ip_container.def

    scp cartpole.sif <SLURM HOST>:/path/syndeo/containers/cartpole.sif
    scp ip.sif <SLURM HOST>:/path/syndeo/containers/ip.sif


To run tests:

.. code-block:: console

    conda activate syndeo
    pytest


The PyTests will generate log files to a :code:`logs/` directory. The tests will read the logs and search for keywords like :code:`sucessfully executed` indicate that the python program succeeded.

If you want to run individual tests using PyTest you can do:

.. code-block:: console

    pytest tests/ip_test.py::<individual_test>


Pytest supports breakpoint `debugging <https://docs.pytest.org/en/6.2.x/usage.html#setting-breakpoints>`_ which can be used to isolate problems.

Pytest Directories
******************

* :ref:`tests/README`.: Primary execution points for PyTests.
* :ref:`tests/scripts/README` : Bash scripts executed during PyTests.
* :ref:`tests/python/README` : Python scripts executed during PyTests.

Nox Testing
***********
Nox is recommended if you want to run your tests in a clean environment from start to finish.  Often times the developer environment is not where you need the tests to succeed, rather you want these tests to succeed on a clean install where other users may want to utilize.  If that is the case make sure your Nox tests pass:

.. code-block:: console

    nox -s pytest
