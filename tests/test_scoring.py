"""Tests for the Nexus Sovereignty Score engine and CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from nss.scoring import NSSInputError, load_definition, score, validate_input

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_INPUT = ROOT / "examples" / "municipality-example.json"
EXAMPLE_OUTPUT = ROOT / "examples" / "municipality-example.output.json"


def _best_answers(definition: dict) -> dict:
    dimensions = {}
    for dimension_id, dimension_def in definition["dimensions"].items():
        answers = {}
        for criterion in dimension_def["criteria"]:
            if criterion.get("answer_type") == "number":
                answers[criterion["id"]] = 0.0
            else:
                best_level = max(
                    (
                        (level, value)
                        for level, value in criterion["levels"].items()
                        if value is not None
                    ),
                    key=lambda item: item[1],
                )[0]
                answers[criterion["id"]] = best_level
        dimensions[dimension_id] = {"answers": answers}
    return {
        "nss_version": "0.1",
        "organisation": {
            "name": "Best Case Org",
            "type": "test",
            "country": "DE",
        },
        "assessment_date": "2026-01-01",
        "dimensions": dimensions,
    }


def _worst_answers(definition: dict) -> dict:
    dimensions = {}
    for dimension_id, dimension_def in definition["dimensions"].items():
        answers = {}
        for criterion in dimension_def["criteria"]:
            if criterion.get("answer_type") == "number":
                answers[criterion["id"]] = 1.0
            else:
                worst_level = min(
                    (
                        (level, value)
                        for level, value in criterion["levels"].items()
                        if value is not None
                    ),
                    key=lambda item: item[1],
                )[0]
                answers[criterion["id"]] = worst_level
        dimensions[dimension_id] = {"answers": answers}
    return {
        "nss_version": "0.1",
        "organisation": {
            "name": "Worst Case Org",
            "type": "test",
            "country": "DE",
        },
        "assessment_date": "2026-01-01",
        "dimensions": dimensions,
    }


def test_dimension_and_criterion_weights_sum_to_one():
    definition = load_definition()
    dimension_total = sum(dim["weight"] for dim in definition["dimensions"].values())
    assert abs(dimension_total - 1.0) < 1e-9
    for dimension_id, dimension_def in definition["dimensions"].items():
        criterion_total = sum(c["weight"] for c in dimension_def["criteria"])
        assert abs(criterion_total - 1.0) < 1e-9, dimension_id


def test_all_best_answers_score_100_grade_a():
    definition = load_definition()
    result = score(_best_answers(definition), definition)
    assert result["composite_score"] == 100
    assert result["grade"] == "A"
    for dimension in result["dimensions"].values():
        assert dimension["score"] == 100.0
        assert dimension["capped"] is False


def test_all_worst_answers_score_0_grade_e():
    definition = load_definition()
    result = score(_worst_answers(definition), definition)
    assert result["composite_score"] == 0
    assert result["grade"] == "E"


def test_critical_cap_limits_dimension_to_40():
    definition = load_definition()
    assessment = _best_answers(definition)
    assessment["dimensions"]["key_management"]["answers"]["KM1"] = "provider"
    result = score(assessment, definition)
    km = result["dimensions"]["key_management"]
    assert km["capped"] is True
    assert km["score"] == 40.0


def test_not_applicable_ai_inference_redistributes_weights():
    definition = load_definition()
    assessment = _best_answers(definition)
    assessment["dimensions"]["ai_inference"] = {"not_applicable": True, "answers": {}}
    result = score(assessment, definition)
    ai = result["dimensions"]["ai_inference"]
    assert ai["not_applicable"] is True
    assert ai["score"] is None
    assert ai["applied_weight"] == 0.0
    applied = [
        dim["applied_weight"]
        for dim_id, dim in result["dimensions"].items()
        if not dim.get("not_applicable")
    ]
    assert abs(sum(applied) - 1.0) < 1e-9
    assert result["composite_score"] == 100
    assert result["grade"] == "A"


def test_null_levels_excluded_for_rm3_and_rm4():
    definition = load_definition()
    assessment = _best_answers(definition)
    assessment["dimensions"]["regulatory_mapping"]["answers"]["RM3"] = "not_in_scope"
    assessment["dimensions"]["regulatory_mapping"]["answers"]["RM4"] = "no_ai_systems"
    result = score(assessment, definition)
    rm = result["dimensions"]["regulatory_mapping"]
    assert rm["criteria"]["RM3"]["not_applicable"] is True
    assert rm["criteria"]["RM4"]["not_applicable"] is True
    assert rm["criteria"]["RM3"]["score"] is None
    assert rm["criteria"]["RM4"]["score"] is None
    remaining = [
        item["applied_weight"]
        for criterion_id, item in rm["criteria"].items()
        if not item.get("not_applicable")
    ]
    assert abs(sum(remaining) - 1.0) < 1e-9
    assert rm["score"] == 100.0


def test_vi4_numeric_scoring_and_range_validation():
    definition = load_definition()
    assessment = _best_answers(definition)
    assessment["dimensions"]["vendor_independence"]["answers"]["VI4"] = 0.25
    result = score(assessment, definition)
    assert result["dimensions"]["vendor_independence"]["criteria"]["VI4"]["score"] == 75.0

    bad = deepcopy(assessment)
    bad["dimensions"]["vendor_independence"]["answers"]["VI4"] = 1.5
    with pytest.raises(NSSInputError, match="between 0.0 and 1.0"):
        validate_input(bad, definition)


def test_invalid_dimension_criterion_and_level_raise():
    definition = load_definition()
    assessment = _best_answers(definition)

    unknown_dimension = deepcopy(assessment)
    unknown_dimension["dimensions"]["not_a_dimension"] = {"answers": {}}
    with pytest.raises(NSSInputError, match="Unknown dimension"):
        validate_input(unknown_dimension, definition)

    unknown_criterion = deepcopy(assessment)
    unknown_criterion["dimensions"]["data_residency"]["answers"]["DR99"] = "eu_eea"
    with pytest.raises(NSSInputError, match="Unknown criterion"):
        validate_input(unknown_criterion, definition)

    invalid_level = deepcopy(assessment)
    invalid_level["dimensions"]["data_residency"]["answers"]["DR1"] = "moon"
    with pytest.raises(NSSInputError, match="Invalid level"):
        validate_input(invalid_level, definition)


def test_municipality_example_matches_committed_output():
    assessment = json.loads(EXAMPLE_INPUT.read_text(encoding="utf-8"))
    expected = json.loads(EXAMPLE_OUTPUT.read_text(encoding="utf-8"))
    result = score(assessment)
    result.pop("generated_at", None)
    expected.pop("generated_at", None)
    assert result == expected


def test_cli_score_success_and_invalid_exit_codes(tmp_path: Path):
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text(
        json.dumps(
            {
                "nss_version": "0.1",
                "organisation": {"name": "X", "type": "t", "country": "DE"},
                "assessment_date": "2026-01-01",
                "dimensions": {},
            }
        ),
        encoding="utf-8",
    )

    ok = subprocess.run(
        [sys.executable, "-m", "nss", "score", str(EXAMPLE_INPUT)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert ok.returncode == 0
    payload = json.loads(ok.stdout)
    assert payload["grade"] in {"C", "D"}

    bad = subprocess.run(
        [sys.executable, "-m", "nss", "score", str(invalid_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad.returncode == 2
    assert "Missing dimension" in bad.stderr
