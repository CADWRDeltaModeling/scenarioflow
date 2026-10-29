"""A single component of a conceptual input."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from vtools.data.timeseries import to_dataframe

from scenarioflow.expressions import _substitute_scalars


@dataclass
class Component:
    """One ordered piece of a series.

    A ``data`` component reads with a named reader (``load_method``) and applies
    named transforms in order. A ``function`` component calls a named function
    (``method``) with ``args``, which usually refer to earlier components via
    ``$!{...}``.
    """

    name: str
    type: str
    effective: Optional[str] = None
    load_method: Optional[Dict[str, Any]] = None
    method: Optional[str] = None
    transformations: List[Dict[str, Any]] = field(default_factory=list)
    args: Dict[str, Any] = field(default_factory=dict)

    def run(self,
            defines: Dict[str, Any],
            workspace: Dict[str, Any],
            readers: Dict[str, Callable[..., Any]],
            transforms: Dict[str, Callable[..., Any]],
            functions: Dict[str, Callable[..., Any]]) -> Any:
        local_dict = {
            "effective": self.effective,
            "load_method": self.load_method,
            "method": self.method,
            "transformations": self.transformations,
            "args": self.args,
        }
        local = _substitute_scalars(local_dict, defines, workspace)

        if self.type == "data":
            if not local["load_method"] or "name" not in local["load_method"]:
                raise ValueError(f"Component '{self.name}': data component requires load_method.name")
            reader_name = local["load_method"]["name"]
            reader_args = {k: v for k, v in (local["load_method"].get("args", {}) or {}).items()}
            if "source" in local["load_method"]:
                if reader_name == "read_csv":
                    reader_args["source"] = local["load_method"]["source"]
                elif reader_name == "read_climatology":
                    reader_args["source"] = local["load_method"]["source"]
                else:
                    reader_args["fpath"] = local["load_method"]["source"]
            reader = readers[reader_name]
            data = reader(**reader_args)
            #data = _ensure_datetime_index(data)
            for t in local["transformations"] or []:
                tname = t.get("name")
                targ  = t.get("args", {}) or {}
                if tname not in transforms:
                    raise ValueError(f"Component '{self.name}': unknown transform '{tname}'")
                fn = transforms[tname]
                data = fn(data, **targ)
            return to_dataframe(data)

        elif self.type == "function":
            method = local.get("method")
            if not method:
                raise ValueError(f"Component '{self.name}': function component requires 'method'")
            func = functions[method]
            fargs = local.get("args", {}) or {}
            return func(**fargs)
        else:
            raise ValueError(f"Component '{self.name}': unknown type '{self.type}'")
