"""Loading of scenario YAML."""

from __future__ import annotations

from typing import Any, Dict, Union

from omegaconf import OmegaConf


def load_yaml(path_or_dict: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Load a scenario configuration without resolving OmegaConf interpolation.

    Parameters
    ----------
    path_or_dict : str or dict
        YAML file path, or an already-loaded dict (returned unchanged).

    Returns
    -------
    dict
        Plain-container configuration.
    """
    if isinstance(path_or_dict, dict):
        return path_or_dict
    cfg = OmegaConf.to_container(OmegaConf.load(path_or_dict), resolve=False)
    return cfg
