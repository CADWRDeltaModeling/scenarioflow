Design
======

``scenarioflow`` is a framework for assembling the time-dependent inputs
to numerical models from sources that differ in provenance, certainty,
duration, and resolution.

The central idea is that a **scenario is not usually one data set**. A
model input such as a river flow, gate operation, stage boundary, or
planning assumption may be assembled from several pieces:

1. a historical archive, often representing the highest-quality
   hindcast data;
2. a real-time or provisional head attached to that archive, possibly
   including short extrapolations; and
3. a forecast, climatology, or planning assumption that carries the
   scenario into the future.

``scenarioflow`` makes that assembly explicit. Each conceptual input is
built independently, normalized (e.g., convert units, rename columns,
and resample from hourly to the scenarioâ€™s 15-minute interval) to a
common representation, spliced together in time with context-appropriate
transitions and only then handed to a **model porter** that knows how to
package the scenario for a particular model.

Design in one picture
---------------------

.. mermaid::

   flowchart LR
       subgraph Sources["Source material"]
           H["Historical archive"]
           R["Real-time / provisional"]
           F["Forecast / planning assumption"]
       end

       subgraph Build["Build conceptual inputs"]
           RD["Readers"]
           TR["Transforms<br/>units, naming, interpolation,<br/>sampling, derived quantities"]
           ST["Splice / transition / extrapolate"]
           CI["Canonical conceptual input<br/>consistent units, structure,<br/>time window and resolution"]
       end

       subgraph Port["Model-specific porting"]
           MP["Model porter<br/>validate â€¢ group â€¢ complete â€¢ render"]
           D["DSM2 inputs"]
           S["SCHISM inputs"]
           O["Other model"]
       end

       H --> RD
       R --> RD
       F --> RD
       RD --> TR
       TR --> ST
       ST --> CI
       CI --> MP
       MP --> D
       MP --> S
       MP --> O

The important boundary is between **scenario construction** and **model
rendering**. Upstream of that boundary, the vocabulary should describe
the physical or operational inputs we mean. Downstream, the porter deals
with the peculiarities of a modelâ€™s input format.

Conceptual pipeline
-------------------

1. Read source material
~~~~~~~~~~~~~~~~~~~~~~~

A **reader** turns an external source into a usable time series or
related object. Sources may include repositories, CSV files, databases,
APIs, scripts, climatologies, or forecast products.

Readers should be small adapters. Their job is to understand the source,
not the target model.

Examples already present in the prototype include repository time-series
readers, ordinary CSV input, and climatology input.

2. Transform components
~~~~~~~~~~~~~~~~~~~~~~~

A source often needs to be transformed before it can participate in a
scenario. Typical transformations include:

- unit conversion;
- column or variable naming;
- temporal interpolation or resampling;
- application of climatology;
- clipping to a useful time window;
- conversion to a common internal representation; and
- derived quantities or other user-defined transformations.

A component may begin at a different resolution from the final model
input. The framework should therefore distinguish the **native
resolution of a source** from the **target resolution of the conceptual
input**.

3. Splice components into one conceptual input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A conceptual input can contain several ordered components. For example:

.. code:: text

   historical archive
       -> transition
   real-time / forecast series
       -> extrapolation or climatology
   planning horizon

The splice is part of the scenario definition, not an accidental side
effect of file precedence. Effective dates and transition rules should
be visible in configuration so that a scenario can be inspected and
reproduced.

The current prototype follows this pattern: data components are loaded
and transformed, function components can create transitions or
extrapolations, and the resulting segments are stitched into a final
series.

4. Normalize the conceptual input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before model-specific rendering, each conceptual input should satisfy a
canonical contract. The exact contract still needs to be formalized, but
it should include at least:

- a stable conceptual name;
- a defined time window;
- a target temporal resolution;
- explicit units;
- a known data shape and column convention;
- provenance for the contributing components;
- explicit missing-data semantics; and
- enough metadata for the porter to determine model placement.

This is the layer that allows scenario construction to remain largely
independent of DSM2, SCHISM, or another model.

5. Port the scenario to a model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A **model porter** consumes the completed conceptual inputs and renders
the files or objects required by a target model.

The porter owns model-specific knowledge. This includes more than file
formatting. It should also know the modelâ€™s required **groups**,
dependencies, and completeness rules.

For example, a SCHISM porter may need to collect all flux boundaries
into the structures expected by SCHISM and separately collect
hydraulic-structure parameters. A DSM2 porter may require a different
grouping and may not consume exactly the same set of conceptual inputs.

The porter should therefore be responsible for:

- mapping conceptual inputs to model-specific names and locations;
- grouping related inputs where the model requires grouped output;
- checking that required members of each group are present;
- rejecting incompatible units, shapes, or resolutions that escaped
  normalization;
- applying model-specific defaults only where those defaults are
  intentional and documented; and
- writing the final model input representation.

A porter is consequently both a **renderer** and a **model-aware
validator**.

Model-independent does not mean lowest common denominator
---------------------------------------------------------

The goal is not to force DSM2 and SCHISM to have identical inputs. They
describe systems differently and have different configuration
requirements.

Instead, ``scenarioflow`` should make the shared conceptual layer as broad
as is useful while allowing model-specific branches at the porting
stage.

One possible mechanism is an explicit **pass-through** conceptual input:
data that scenarioflow carries, validates minimally, and makes available
to a porter even when it has no universal interpretation. This can
accommodate model-specific information without contaminating the general
scenario-building machinery.

Pass-through data should remain explicit. It should not become a hidden
escape hatch that bypasses validation for ordinary time series.

Extension model
---------------

The framework should be extensible without requiring every
domain-specific reader, transformation, or porter to live in the
``scenarioflow`` package.

User-installed packages should be able to contribute:

- **readers** â€” adapters for repositories, databases, forecast
  products, APIs, and local formats;
- **transforms** â€” domain-specific normalization, interpolation,
  conversions, and derived quantities;
- **functions/stitchers** â€” transitions, extrapolators, and other
  ways of constructing components; and
- **model porters** â€” validation, grouping, mapping, and rendering
  for a particular model; and
- **viewers** â€” optional domain-specific inspection views for
  conceptual inputs or groups.

A small core registry can provide built-ins, while plugins register
additional named implementations. Configuration then refers to those
implementations by stable names rather than importing arbitrary Python
in YAML.

Conceptually:

.. code:: text

   scenarioflow core
       readers registry
       transforms registry
       functions/stitchers registry
       porters registry
       viewers registry
             ^
             |
       installed user packages

For a mature implementation, Python entry points are a natural discovery
mechanism for installed plugins. Direct registration through a Python
API is also useful for development and testing.

Configuration sketch
--------------------

The existing YAML already expresses the component-oriented part of the
design. A future extension could make the target model and porter
explicit:

.. code:: yaml

   define:
     session_start: 2025-04-01
     session_end: 2025-12-31
     flux_dt: 15min

   scenario:
     name: example
     defaults:
       dt_target: ${flux_dt}

     series:
       - name: sac
         components:
           - name: hist
             type: data
             effective: ${session_start}
             load:
               name: read_ts_repo
               args: {...}
             transformations:
               - name: unit_conversion
                 args: {from_unit: "ft^3/s", to_unit: "m^3/s"}

           - name: forecast
             type: data
             effective: ${forecast_start}
             load:
               name: read_forecast_product
               args: {...}

         stitcher:
           name: ts_splice
           args: {}

   targets:
     - porter: schism
       output: ./schism_inputs
       mapping: schism_mapping.yml

     - porter: dsm2
       output: ./dsm2_inputs
       mapping: dsm2_mapping.yml

The exact schema is not settled by this example. In particular,
model-specific mapping may belong in a separate file so that a scenario
can be reused with several models without embedding their details in the
conceptual scenario definition.

Example use cases
-----------------

The component-and-assembly model is easiest to understand through a few
common operational cases.

Use case 1: extend a hindcast lightly to tomorrow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A frequently needed scenario is not really a forecast. The historical or
provisional record is nearly current, but the model input needs to reach
tomorrow. A short extension can be constructed explicitly rather than
modifying the archive itself.

For example:

.. code:: text

   historical / provisional archive
           |
           +-- ffill for a short gap
           |
           +-- climatology, if a longer or seasonally varying extension is preferred
           |
         tomorrow

A particular series might use only ``ffill``, only climatology, or both in
sequence:

.. code:: text

   archive through Aug 10 12:00
       -> ffill through Aug 11 00:00
       -> climatology through Aug 13

These operations have different meanings. ``ffill`` says, in effect, â€œhold
the most recent value for this short operational gap.â€ Applying
climatology substitutes an expected seasonal pattern. Scenarioflow
should keep those choices explicit in the construction recipe.

The **Assembly Preview** should make the construction visible: show the
source component, the extension, the final assembled series, and markers
or shading at the effective dates and transition regions. This is
construction/lineage information, not an assertion of uniquely defined
pointwise provenance.

Use case 2: append a three-week operational forecast
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A second common case is a hindcast or provisional archive followed by a
genuine operational forecast:

.. code:: text

   historical / provisional archive
                 |
                 | forecast effective time
                 v
         operational forecast
                 |
                 v
            +21 days

Here the forecast is a data component with its own reader, not merely an
extrapolation method. The stitcher determines how the historical and
forecast components are assembled.

Forecast products may overlap the archive. That overlap can support
several explicit policies:

- switch to the forecast at a specified effective time;
- blend over a short transition window; or
- continue to prefer observations/provisional data where available and
  use the forecast beyond their endpoint.

The policy belongs to scenario assembly rather than to either reader.
Readers retrieve candidate components; the stitcher controls precedence
and transition.

Configurable components
~~~~~~~~~~~~~~~~~~~~~~~

Scenarioflow should support reusable scenario recipes whose details are
supplied through configuration rather than hard-coded into the component
implementation.

There are two useful kinds of configuration.

**Parameters** are known before execution. Examples include station
names, paths, target resolution, forecast horizon, transition duration,
units, and scenario dates. The current ``${...}`` substitution mechanism
supports values from the scenario ``define`` block and environment
variables.

.. code:: yaml

   define:
     forecast_days: 21
     transition_hours: 6
     dt_target: 15min
     station: Station1

**Workspace references or expressions** refer to objects or values
produced while the scenario is being assembled. The current ``$!{...}``
mechanism supports this distinction. For example, an extrapolator can
refer to an already loaded historical series or derive its starting
point from the endpoint of that series.

The GUI does not need to expose the expression syntax for routine cases.
A Panel editor can present semantic controls such as:

.. code:: text

   Component: short_extension

   Method          extrapolate_ts
   Input series    Station1.hist
   Method          ffill
   Start           End of input series
   End             Scenario end

and serialize those selections to the corresponding YAML representation.

Similarly, a forecast component could expose:

.. code:: text

   Component: ops_forecast

   Type            Data
   Reader          operational_forecast
   Station         Station1
   Issue           Latest available
   Horizon         21 days
   Effective       Forecast start

For contributed readers and transforms, a useful plugin contract is
therefore somewhat richer than a callable alone. A plugin can advertise:

.. code:: text

   name
   callable
   parameter schema
   description
   optional output metadata

The parameter schema gives the same component definition three natural
front ends:

.. code:: text

   YAML             CLI             Panel GUI
     \               |               /
      +--------------+--------------+
                     |
             scenarioflow component

YAML remains the durable, reviewable scenario representation. The GUI is
an editor and inspector for that representation rather than a separate
configuration system.

Inspection and GUI design
-------------------------

A GUI should expose the same scenario definition used by YAML and the
Python API rather than create a separate configuration system.
Panel/Bokeh is a natural frontend for this because the application is
primarily an editor and inspector for Python objects and time series.

The basic interaction should remain simple:

.. code:: text

   navigation        one active viewer             inspector
       |                    |                          |
   group / input  -> selected conceptual input -> selected object/component

The navigation hierarchy is approximately **group -> conceptual input
-> component**. Groups might include flows, elevation, temperature,
salinity, structures, and sources/sinks. Selecting a group should
provide a compact overview and validation status; selecting one
conceptual input opens its appropriate detailed viewer.

Time-series assembly view
~~~~~~~~~~~~~~~~~~~~~~~~~

Ordinary time-dependent inputs such as flow, temperature, salinity, and
elevation should share a standard assembly viewer with at least two
modes:

- **Final** â€” the assembled conceptual input, with the assembly
  track and transition boundaries visible; and
- **Components** â€” the contributing component series together with
  the final splice and the same assembly track.

The assembly track is important in both modes because it shows how the
final series was constructed: historical, provisional, transition,
forecast, climatology, extrapolation, or other components. Transition
windows and effective dates should be visible without implying uniquely
defined pointwise provenance.

A configuration/inspection mode can expose the selected reader,
transforms, effective dates, stitcher, target resolution, and validation
messages.

Group views and model grouping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The GUI should not attempt to plot every member of a model group at
once. A group-level view is primarily for navigation, coverage, and
completeness checking. For example, a SCHISM flow group might show ten
named inputs with their time coverage, abbreviated assembly recipe, and
validation status. Selecting one flow then opens its detailed assembly
view.

This distinction also mirrors the porter architecture: conceptual inputs
are constructed individually, while the model porter knows which
completed inputs must ultimately be grouped together and can report
missing or incompatible members.

Registered viewers for nonstandard inputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not every conceptual input is best represented by a single line plot.
The GUI should therefore allow installed packages to contribute
**viewers** in addition to readers, transforms, stitchers, and porters.

Examples include:

- a standard time-series assembly viewer;
- a mixed-type hydraulic-structure viewer, where integer state,
  continuous height, and bounded operation fraction can share a time
  axis but use appropriate separate tracks; and
- a source/sink viewer suitable for navigating a large collection of
  inputs.

A viewer should attach to the conceptual input type or group rather than
to a reader. Readers retrieve data; viewers display assembled objects
and, when useful, their components.

Conceptually:

.. code:: text

   scenarioflow GUI shell
           |
           +-- navigation
           +-- registered viewer for current selection
           +-- inspector / configuration

Only one primary viewer needs to be active at a time. Selecting a flow,
structure, or source/sink changes the center view rather than adding
another dashboard panel.

Spatial information
~~~~~~~~~~~~~~~~~~~

Some input collections, especially large sets of sources and sinks, have
a useful spatial representation. The design should preserve stable
identifiers and allow optional geometry or spatial metadata so that a
lightweight map viewer or an external GIS can be used later. Spatial
editing and GIS behavior do not need to be part of the scenarioflow
core; the important architectural point is to avoid preventing such
integration.

Plugin metadata for configuration and display
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A contributed plugin should eventually advertise more than a callable.
Useful registration metadata includes:

.. code:: text

   name
   callable
   parameter schema
   description
   optional output/type metadata
   optional viewer

The parameter schema allows YAML, command-line tools, and a GUI to
configure the same implementation consistently. The optional type/viewer
metadata allows the GUI to choose an appropriate display without putting
domain-specific visualization logic into the core.

Proposed internal architecture
------------------------------

A useful separation of responsibilities is:

.. code:: text

   Scenario
     |
     +-- ConceptualInput / SeriesSpec
     |     |
     |     +-- Component
     |     |     +-- Reader
     |     |     +-- Transform(s)
     |     |     +-- effective time / provenance
     |     |
     |     +-- Stitcher / transition / extrapolator
     |     +-- Canonicalization
     |
     +-- Validation of model-independent invariants
     |
     +-- ModelPorter
           +-- model-specific mapping
           +-- grouping
           +-- completeness checks
           +-- rendering

This preserves a useful rule:

   **Readers know sources. Transforms know data operations. Scenario
   assembly knows time and precedence. Porters know models.**

Keeping those responsibilities separate is what makes contributions from
other packages tractable.

Validation and construction lineage
-----------------------------------

Because scenarios mix observed, provisional, forecast, and assumed data,
the construction recipe should remain inspectable and reproducible. This
does not imply that provenance is uniquely defined pointwise in time
after interpolation, blending, resampling, climatology, or other
transformations.

A finished conceptual input should retain enough component-level lineage
to answer questions such as:

- which source components and operations were used to construct the
  input;
- what their nominal or effective ranges and roles were;
- what source and reader produced each component;
- which transforms were applied;
- where transitions or extrapolations were introduced;
- what the native resolution of the components was; and
- what resolution was delivered to the porter.

The useful invariant is reproducible construction history, not a
provenance label attached to every output value.

Validation should occur at two levels:

**Scenario-level validation** checks model-independent invariants such
as time coverage, monotonic indexes, units, target resolution, and
missing data.

**Porter-level validation** checks model-specific completeness and
compatibility, including required groups.

Current prototype
-----------------

The current implementation already establishes several pieces of this
architecture:

- named reader, transform, and function registries;
- ``Component``, ``SeriesSpec``, and ``Scenario`` objects;
- data components followed by function components;
- workspace references that allow transitions and extrapolations to
  use earlier results;
- configurable stitchers;
- scenario-wide defaults with per-series overrides; and
- a plotting utility for examining components and the final splice.

The next architectural step is not to make the core more model-aware. It
is to formalize the canonical conceptual-input contract and add the
porter/plugin boundary.

Near-term implementation priorities
-----------------------------------

1. Define the canonical output contract of a ``SeriesSpec`` or its
   successor: units, resolution, shape, metadata, provenance, and
   missing-data rules.
2. Introduce a ``ModelPorter`` interface with explicit ``validate()``,
   ``group()``, and ``write()`` responsibilities.
3. Decide how conceptual inputs are mapped to porter inputs, preferably
   outside the core series definitions.
4. Add a plugin registration/discovery mechanism for readers,
   transforms, functions/stitchers, porters, and optional viewers.
5. Preserve component-level construction lineage through splicing and
   extrapolation.
6. Add dry-run/inspection output so contributors can see the resolved
   component graph, effective dates, final coverage, and porter groups
   without writing model files.
7. Add schema validation and actionable error messages before
   execution.
8. Keep the core package deliberately small; domain knowledge belongs
   in plugins and porters.
