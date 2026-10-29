# Configuration file for the Sphinx documentation builder.
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

import scenarioflow  # noqa: E402

project = "scenarioflow"
copyright = "2025-2026, California Department of Water Resources"
author = "Eli Ateljevich"
version = scenarioflow.__version__
release = scenarioflow.__version__

extensions = [
    "sphinx_rtd_theme",
    "sphinxcontrib.mermaid",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_click",
]

napoleon_numpy_docstring = True
napoleon_google_docstring = False
autodoc_member_order = "bysource"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "vtools": ("https://cadwrdeltamodeling.github.io/vtools3/html", None),
    "dms_datastore": ("https://cadwrdeltamodeling.github.io/dms_datastore", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build"]
source_suffix = ".rst"
master_doc = "index"
pygments_style = "sphinx"

html_theme = "sphinx_rtd_theme"
html_theme_options = {"logo_only": False}
html_static_path = ["_static"]
