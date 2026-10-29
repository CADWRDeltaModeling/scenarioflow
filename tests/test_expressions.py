import pandas as pd
import pytest

from scenarioflow.expressions import _safe_eval, _substitute_scalars


def test_define_substitution():
    assert _substitute_scalars("${a}/x", {"a": 1}, {}) == "1/x"


def test_environment_fallback(monkeypatch):
    monkeypatch.setenv("SFLOW_TEST_VAR", "abc")
    assert _substitute_scalars("${SFLOW_TEST_VAR}", {}, {}) == "abc"


def test_undefined_variable_raises():
    with pytest.raises(KeyError, match="nope"):
        _substitute_scalars("${nope}", {}, {})


def test_full_workspace_expression_returns_object():
    ts = pd.Series([1.0, 2.0], index=pd.date_range("2025-01-01", periods=2, freq="D"))
    out = _substitute_scalars("$!{ts.last_valid_index() - days(1)}", {}, {"ts": ts})
    assert out == pd.Timestamp("2025-01-01")


def test_inline_workspace_expression_is_text():
    assert _substitute_scalars("n=$!{x + 1}", {}, {"x": 1}) == "n=2"


def test_nested_structures():
    out = _substitute_scalars({"a": ["${v}", {"b": "$!{w}"}], "c": 3}, {"v": "V"}, {"w": 7})
    assert out == {"a": ["V", {"b": 7}], "c": 3}


def test_builtins_unavailable():
    with pytest.raises(NameError):
        _safe_eval("open('x')", {})
