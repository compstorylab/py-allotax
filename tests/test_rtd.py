"""Tests for in-process RTD computation via the allotax bindings (no node/JS).

py-allotax has no RTD wrapper of its own — users call
`allotax.rank_turbulence_divergence` directly, with `as_system` coercing
their data. These tests pin that pattern and its numbers.
"""

import json
import os

import allotax
import pandas as pd
import pytest

from py_allotax import as_system

DATA_1 = os.path.join("example_data", "boys_2022.json")
DATA_2 = os.path.join("example_data", "boys_2023.json")

# Golden values from the original JS implementation (allotaxonometer-ui)
# on boys_2022 vs boys_2023 with alpha=0.17.
EXPECTED_NORMALIZATION = 1692.7561270411318
EXPECTED_TOTAL_WORDS = 1292


def test_rtd_matches_js_baseline():
    result = allotax.rank_turbulence_divergence(
        as_system(DATA_1), as_system(DATA_2), 0.17, limit=0
    )

    assert result["normalization"] == pytest.approx(EXPECTED_NORMALIZATION)
    assert len(result["wordshift"]) == EXPECTED_TOTAL_WORDS

    top = result["wordshift"][0]
    assert top["type"] == "Grover"
    assert top["rank1"] == 413.5
    assert top["rank2"] == 20.0
    assert top["divergence"] == pytest.approx(0.001209, abs=1e-6)


def test_rtd_accepts_dataframes_and_records():
    with open(DATA_1) as f:
        records1 = json.load(f)
    with open(DATA_2) as f:
        records2 = json.load(f)

    df1, df2 = pd.DataFrame(records1), pd.DataFrame(records2)

    # Key by type: the Rust core's parallel summation is nondeterministic in
    # the last float bits, so the sort order of tied metrics can differ
    # between identical calls.
    def divergences(data1, data2):
        result = allotax.rank_turbulence_divergence(data1, data2, 0.17, limit=0)
        return result["normalization"], {e["type"]: e["divergence"] for e in result["wordshift"]}

    norm_files, from_files = divergences(as_system(DATA_1), as_system(DATA_2))
    norm_dfs, from_dfs = divergences(df1, df2)  # DataFrames go in directly
    norm_records, from_records = divergences(as_system(records1), as_system(records2))

    assert norm_dfs == pytest.approx(norm_files, rel=1e-9)
    assert norm_records == pytest.approx(norm_files, rel=1e-9)
    for other in (from_dfs, from_records):
        assert other.keys() == from_files.keys()
        for word, value in from_files.items():
            assert other[word] == pytest.approx(value, rel=1e-6, abs=1e-12)


def test_rtd_infinity_alpha():
    result = allotax.rank_turbulence_divergence(
        as_system(DATA_1), as_system(DATA_2), float("inf"), limit=5
    )
    assert result["normalization"] > 0
    assert len(result["wordshift"]) == 5
