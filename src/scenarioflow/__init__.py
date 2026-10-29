"""scenarioflow: assemble model input scenarios from historical, real-time,
forecast and planning components."""

import logging

try:
    from scenarioflow._version import __version__
except ImportError:  # running from a source tree that was never installed
    __version__ = "0.0.0"

from scenarioflow.component import Component
from scenarioflow.config import load_yaml
from scenarioflow.scenario import Scenario
from scenarioflow.series import SeriesSpec

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["__version__", "Component", "SeriesSpec", "Scenario", "load_yaml"]
