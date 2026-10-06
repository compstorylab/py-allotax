"""Data coercion and RTD computation helpers."""

import json
import os

import pandas as pd


def parse_alpha(alpha) -> float:
    """Parse an alpha argument ("0.17", "Infinity", 0.17, float("inf")) to float."""
    return float(alpha)


def as_system(data) -> dict:
    """Coerce a supported input into the columnar dict allotax expects.

    Accepts:
        - a path to a .json data file containing a list of records,
        - a pandas DataFrame with 'types' and 'counts' columns,
        - a list of records (dicts with 'types' and 'counts' keys),
        - an already-columnar dict with 'types' and 'counts' lists.

    Returns:
        Dict with 'types' (list[str]) and 'counts' (list[float]).
    """
    if isinstance(data, (str, os.PathLike)):
        try:
            with open(data, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(
                f"Invalid JSON structure in {data}. File should be "
                "a .json wherein the data is a list of dictionaries."
            )
    if isinstance(data, pd.DataFrame):
        missing = {"types", "counts"} - set(data.columns)
        if missing:
            raise ValueError(
                f"DataFrame is missing required column(s): {sorted(missing)}"
            )
        return {
            "types": data["types"].astype(str).tolist(),
            "counts": data["counts"].astype(float).tolist(),
        }
    if isinstance(data, dict):
        if not {"types", "counts"} <= data.keys():
            raise ValueError("dict input must have 'types' and 'counts' keys")
        return {
            "types": [str(t) for t in data["types"]],
            "counts": [float(c) for c in data["counts"]],
        }
    if isinstance(data, list):
        try:
            return {
                "types": [str(r["types"]) for r in data],
                "counts": [float(r["counts"]) for r in data],
            }
        except (TypeError, KeyError):
            raise ValueError(
                "list input must contain records (dicts) with 'types' and 'counts' keys"
            )
    raise TypeError(
        "data must be a path to a .json file, a pandas DataFrame, a list of "
        f"records, or a dict with 'types' and 'counts'; got {type(data).__name__}"
    )


# For RTD data without a plot, call the Rust bindings directly:
#   import allotax
#   allotax.rank_turbulence_divergence(as_system(data1), as_system(data2), 0.17)
# See the README and examples.ipynb.
