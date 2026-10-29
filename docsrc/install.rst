Installation
============

Conda (users)
-------------

.. code-block:: bash

   conda install -c cadwr-dms -c conda-forge scenarioflow

Development
-----------

.. code-block:: bash

   git clone https://github.com/CADWRDeltaModeling/scenarioflow
   cd scenarioflow
   conda env create -f environment.yml
   conda activate scenarioflow
   pip install --no-deps -e .

Run the tests. Tests marked ``integration`` need access to the
``dms_datastore`` repository:

.. code-block:: bash

   pytest -m "not integration"
   pytest                      # include integration tests

Documentation
-------------

The documentation tools are an overlay on the development environment; see the
header of ``environment-doc.yml``. Then:

.. code-block:: bash

   sphinx-build -b html docsrc docs/html
