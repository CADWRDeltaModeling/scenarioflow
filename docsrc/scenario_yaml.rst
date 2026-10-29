Scenario YAML reference
=======================

A scenario file has a ``define:`` block of parameters and a ``scenario:``
block of series. A complete worked example is
``examples/sac_sjr_flux/scenario.yml``.

.. code-block:: yaml

   define:
     session_start: 2025-04-01
     session_end:   2025-12-31
     flux_dt: "15min"

   scenario:
     name: flux
     defaults:
       dt_target: ${flux_dt}
       stitcher: {name: ts_splice, args: {}}
     series:
       - name: sac
         components:
           - name: hist
             type: data
             effective: ${session_start}
             load:
               name: read_ts_repo
               args: {station_id: fpt, variable: flow, start: 2025-03-01}
             transformations:
               - name: unit_conversion
                 args: {from_unit: "ft^3/s", to_unit: "m^3/s"}
           - name: forecast_extrapolation
             type: function
             method: extrapolate_ts
             args:
               ts: $!{hist}
               start: $!{hist.last_valid_index()}
               end: ${session_end}
             effective: $!{hist.last_valid_index()}

Substitution
------------

``${name}``
   A parameter from ``define:``, or else an environment variable. Unknown
   names raise ``KeyError``. The result is text.

``$!{expression}``
   A Python expression evaluated against the *workspace*: outputs of
   components already run, available as ``<component>`` and
   ``<series>.<component>``. Also available: ``days(n)``, ``hours(n)``,
   ``minutes(n)``, ``pd`` and ``math``. Builtins are not available. If the
   whole value is one ``$!{...}`` the object itself is used (e.g. a series or
   timestamp); otherwise its text is inlined.

Execution order
---------------

Within a series, all ``data`` components run first in listed order, then all
``function`` components in listed order. A function component may therefore
refer to any data component of its series. The outputs are then stitched in
listed order.

Scenario keys
-------------

``scenario.name``
   Scenario name.
``scenario.defaults.dt_target`` / ``scenario.dt_target``
   Default target time step for series.
``scenario.defaults.stitcher`` / ``scenario.stitcher``
   Default stitcher for series.
``scenario.series``
   List of series.

Series keys
-----------

``name``
   Series name.
``dt_target``
   Target time step; defaults to the scenario value.
``stitcher``
   ``{name: ..., args: {...}}``. ``ts_splice`` (default) splices at the
   components' effective times; ``ts_merge`` performs a prioritized merge.
   Arguments go to :func:`vtools.functions.merge.ts_splice` or
   :func:`vtools.functions.merge.ts_merge`. For ``ts_splice``, the first
   component is clipped at its own effective time, and ``transition`` defaults
   to the effective times of the remaining components that have one.
``components``
   Ordered list of components.

Component keys
--------------

``name``
   Component name.
``type``
   ``data`` or ``function``.
``effective``
   Time from which the component takes over in the splice. ``start``, an
   empty value or no value means no effective time.
``load`` (data; ``load_method`` is accepted as an alias)
   ``name`` of a reader, optional ``source`` and ``args``. ``source`` is
   passed as ``source=`` to ``read_csv`` and ``read_climatology`` and as
   ``fpath=`` to other readers.
``transformations`` (data)
   Ordered list of ``{name: ..., args: {...}}``.
``method`` and ``args`` (function)
   Function name and keyword arguments.

Built-in readers
----------------

``read_ts``
   ``dms_datastore`` ``read_ts`` on a file.
``read_ts_repo``
   ``dms_datastore`` ``read_ts_repo`` from the repository.
``read_csv``
   :func:`pandas.read_csv`.
``read_climatology``
   CSV climatology indexed by period (e.g. day of year).

Built-in transforms
-------------------

``unit_conversion`` (``from_unit``, ``to_unit``)
   :func:`vtools.functions.unit_conversions.convert_units`.
``rhistinterp`` (``dest``, ``p``)
   Mean-preserving interpolation of period averages to ``dest`` with vtools ``rhistinterp``.
``apply_climatology`` (``start``, ``end``, ``freq``, ``index``)
   Expand a climatology over a time range with vtools ``apply_climatology``.
``rename_columns`` (``colnames``)
   Rename columns.

Built-in functions
------------------

``transition_ts`` (``ts0``, ``ts1``, ``method``, ``window``, ``overlap``, ``return_type``, ...)
   Transition between two series with vtools ``transition_ts``.
``extrapolate_ts`` (``ts``, ``start``, ``end``, ``method="ffill"``)
   Extend a series over ``start``..``end`` by forward fill.

Adding readers, transforms and functions
----------------------------------------

Pass dictionaries in ``extra_namespace`` to
``Scenario.from_config``:

.. code-block:: python

   sc = Scenario.from_config(cfg, extra_namespace={"readers": {"read_mine": read_mine}})
