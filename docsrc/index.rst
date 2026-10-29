scenarioflow
============

``scenarioflow`` assembles the time-dependent inputs to numerical models from
sources that differ in provenance, certainty, duration and resolution:
historical archives, real-time or provisional data, forecasts, climatology and
planning assumptions.

Each conceptual input (a river flow, a gate operation, ...) is built from
ordered *components*, each read and transformed independently, and then
spliced together in time at explicit *effective* dates.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   install
   scenario_yaml
   commands
   design
   api
   changelog
