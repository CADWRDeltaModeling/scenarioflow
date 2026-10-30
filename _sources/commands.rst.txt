Command-line tools
==================

All commands are subcommands of ``sflow``. Every command accepts ``-h``/``--help``
and the common logging options ``--logdir``, ``--debug``, ``-v/--verbose`` and
``-q/--quiet``.

Example, run from ``examples/sac_sjr_flux``:

.. code-block:: bash

   sflow plot scenario.yml -o figs        # figs/sac.png, figs/sjr.png
   sflow plot scenario.yml --series sac --show
   sflow plot scenario.yml --gui          # interactive Assembly Preview mock

.. click:: scenarioflow.__main__:cli
   :prog: sflow
   :nested: full
