Changelog
=========

0.1.0 (unreleased)
------------------

* Packaged the prototype (``ts_scenario.py``, ``run_scenario_plot.py``) as
  ``scenarioflow`` with a ``src`` layout. Scenario behavior is unchanged.
* ``sflow plot`` replaces ``python run_scenario_plot.py``. ``--series`` is now
  repeatable (``--series sac --series sjr``); ``-o/--output`` replaces
  ``--out`` (still accepted).
* Logging through the ``scenarioflow`` logger with the common
  ``--logdir/--debug/-v/-q`` options.
* Sphinx documentation, pytest suite, conda recipe and GitHub Actions.
