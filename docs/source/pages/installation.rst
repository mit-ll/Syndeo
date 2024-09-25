############
Installation
############

These are some variables that should be set prior to running the tests.

.. code-block:: bash

    # Ensure that you are using local python packages
    export PYTHONNOUSERSITE=True

.. note::
   :class: margin

   In order to run this program you will need to create a custom environment.  This assumes you are using Anaconda.

.. code-block:: console

    conda create -n syndeo python=3.10
    conda activate syndeo
    pip install poetry # ensure your version is >= 1.4.2
    poetry install # add --with=dev if you want developer tests

.. tip::

   If you would rather use the pip installer executing the following instead.

.. code-block:: console

    pip install .

Documentation
**************

To generate the full documentation use Sphinx [#]_.

.. code-block:: console

   nox -rs show_sphinx

..
   Footnotes
.. rubric:: Footnotes

.. [#] This will generate a ``index.html`` under ``docs/build/index.html``.
