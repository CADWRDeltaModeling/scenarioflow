scenarioflow
============

Assemble the time-dependent inputs to numerical models from historical,
real-time, forecast, climatology and planning components.

A scenario is not usually one data set. A model input such as a river flow may
be a historical archive, joined to a provisional or real-time head, followed by
a forecast or planning assumption. ``scenarioflow`` makes that assembly explicit
in a YAML recipe: each component is read and transformed independently, then
spliced in time at visible effective dates.

* Documentation: https://cadwrdeltamodeling.github.io/scenarioflow
* Source: https://github.com/CADWRDeltaModeling/scenarioflow

Quick start
-----------

.. code-block:: bash

   conda install -c cadwr-dms -c conda-forge scenarioflow
   cd examples/sac_sjr_flux
   sflow plot scenario.yml -o figs

.. code-block:: python

   from scenarioflow import Scenario, load_yaml

   sc = Scenario.from_config(load_yaml("scenario.yml"))
   results = sc.run()          # {"sac": DataFrame, "sjr": DataFrame}

License
-------

MIT. See ``LICENSE``.
