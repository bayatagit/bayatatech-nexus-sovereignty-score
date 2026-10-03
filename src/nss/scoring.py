"""Scoring engine for the Nexus Sovereignty Score."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from importlib import resources
from typing import Any


class NSSInputError(ValueError):
    """Raised when assessment input fails validation."""


def load_definition(path: str | None = None) -> dict[str, Any]:
    """Load a scoring definition JSON document.

    When *path* is omitted, the bundled ``nss-scoring-v0.1.json`` is used.
    """
    if path is None:
        definition_file = resources.files("nss.data").joinpath("nss-scoring-v0.1.json")
        with definition_file.open(encoding="utf-8") as handle:
            return json.load(handle)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def validate_input(data: dict[str, Any], definition: dict[str, Any]) -> None:
    """Validate assessment input against the scoring definition.

    Raises:
        NSSInputError: on unknown dimensions/criteria, invalid levels,
            missing answers, or out-of-range numeric values.
    """
    if not isinstance(data, dict):
        raise NSSInputError("Assessment input must be a JSON object")

    for key in ("nss_version", "organisation", "assessment_date", "dimensions"):
        if key not in data:
            raise NSSInputError(f"Missing required field: {key}")

    organisation = data["organisation"]
    if not isinstance(organisation, dict):
        raise NSSInputError("organisation must be an object")
    for key in ("name", "type", "country"):
        if key not in organisation or not isinstance(organisation[key], str) or not organisation[key].strip():
            raise NSSInputError(f"organisation.{key} must be a non-empty string")

    dimensions = data["dimensions"]
    if not isinstance(dimensions, dict):
        raise NSSInputError("dimensions must be an object")

    known_dimensions = definition["dimensions"]
    for dimension_id in dimensions:
        if dimension_id not in known_dimensions:
            raise NSSInputError(f"Unknown dimension: {dimension_id}")

    for dimension_id, dimension_def in known_dimensions.items():
        if dimension_id not in dimensions:
            raise NSSInputError(f"Missing dimension: {dimension_id}")
        dim_input = dimensions[dimension_id]
        if not isinstance(dim_input, dict):
            raise NSSInputError(f"Dimension {dimension_id} must be an object")

        not_applicable = bool(dim_input.get("not_applicable", False))
        answers = dim_input.get("answers", {})
        if answers is None:
            answers = {}
        if not isinstance(answers, dict):
            raise NSSInputError(f"Dimension {dimension_id} answers must be an object")

        criteria_by_id = {criterion["id"]: criterion for criterion in dimension_def["criteria"]}
        for criterion_id in answers:
            if criterion_id not in criteria_by_id:
                raise NSSInputError(
                    f"Unknown criterion {criterion_id} in dimension {dimension_id}"
                )

        if not_applicable:
            continue

        for criterion in dimension_def["criteria"]:
            criterion_id = criterion["id"]
            if criterion_id not in answers:
                raise NSSInputError(
                    f"Missing answer for criterion {criterion_id} in dimension {dimension_id}"
                )
            answer = answers[criterion_id]
            _validate_answer(dimension_id, criterion, answer)


def _validate_answer(dimension_id: str, criterion: dict[str, Any], answer: Any) -> None:
    criterion_id = criterion["id"]
    if criterion.get("answer_type") == "number":
        if not isinstance(answer, (int, float)) or isinstance(answer, bool):
            raise NSSInputError(
                f"Criterion {criterion_id} in {dimension_id} requires a number"
            )
        minimum = criterion["min"]
        maximum = criterion["max"]
        if answer < minimum or answer > maximum:
            raise NSSInputError(
                f"Criterion {criterion_id} in {dimension_id} must be between "
                f"{minimum} and {maximum}, got {answer}"
            )
        return

    levels = criterion.get("levels", {})
    if not isinstance(answer, str):
        raise NSSInputError(
            f"Criterion {criterion_id} in {dimension_id} requires a string level"
        )
    if answer not in levels:
        allowed = ", ".join(sorted(levels))
        raise NSSInputError(
            f"Invalid level '{answer}' for criterion {criterion_id} in "
            f"{dimension_id}; allowed: {allowed}"
        )


def _criterion_score(criterion: dict[str, Any], answer: Any) -> float | None:
    if criterion.get("answer_type") == "number":
        return float(round(100 * (1 - float(answer))))
    level_score = criterion["levels"][answer]
    if level_score is None:
        return None
    return float(level_score)


def _redistribute_weights(items: list[tuple[str, float]]) -> dict[str, float]:
    total = sum(weight for _, weight in items)
    if total <= 0:
        raise NSSInputError("No applicable weights remain after exclusions")
    return {item_id: weight / total for item_id, weight in items}


def _grade_for_score(composite: int, grades: dict[str, Any]) -> str:
    for letter in ("A", "B", "C", "D", "E"):
        band = grades[letter]
        if band["min"] <= composite <= band["max"]:
            return letter
    raise NSSInputError(f"Composite score {composite} outside grade bands")


def score(
    data: dict[str, Any],
    definition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Score an assessment and return a result matching the output schema."""
    if definition is None:
        definition = load_definition()
    validate_input(data, definition)

    rules = definition["rules"]
    critical_cap = rules["critical_cap"]
    finding_threshold = rules["finding_threshold"]
    grades = rules["grades"]
    dimension_rounding = rules["rounding"]["dimension"]
    composite_rounding = rules["rounding"]["composite"]

    dimension_results: dict[str, Any] = {}
    applicable_dimension_weights: list[tuple[str, float]] = []
    findings: list[dict[str, Any]] = []

    for dimension_id, dimension_def in definition["dimensions"].items():
        dim_input = data["dimensions"][dimension_id]
        if dim_input.get("not_applicable", False):
            dimension_results[dimension_id] = {
                "score": None,
                "applied_weight": 0.0,
                "capped": False,
                "not_applicable": True,
                "criteria": {},
            }
            continue

        answers = dim_input.get("answers", {})
        applicable_criteria: list[tuple[dict[str, Any], Any, float]] = []
        criteria_output: dict[str, Any] = {}

        for criterion in dimension_def["criteria"]:
            criterion_id = criterion["id"]
            answer = answers[criterion_id]
            criterion_value = _criterion_score(criterion, answer)
            if criterion_value is None:
                criteria_output[criterion_id] = {
                    "score": None,
                    "applied_weight": 0.0,
                    "not_applicable": True,
                    "answer": answer,
                }
                continue
            applicable_criteria.append((criterion, answer, criterion_value))

        if not applicable_criteria:
            raise NSSInputError(
                f"Dimension {dimension_id} has no applicable criteria"
            )

        applied_criterion_weights = _redistribute_weights(
            [(criterion["id"], criterion["weight"]) for criterion, _, _ in applicable_criteria]
        )

        weighted_sum = 0.0
        critical_zero = False
        for criterion, answer, criterion_value in applicable_criteria:
            criterion_id = criterion["id"]
            applied_weight = applied_criterion_weights[criterion_id]
            weighted_sum += criterion_value * applied_weight
            criteria_output[criterion_id] = {
                "score": criterion_value,
                "applied_weight": applied_weight,
                "not_applicable": False,
                "answer": answer,
            }
            if criterion.get("critical") and criterion_value == 0:
                critical_zero = True
            if criterion_value < finding_threshold:
                findings.append(
                    {
                        "dimension": dimension_id,
                        "criterion": criterion_id,
                        "score": criterion_value,
                        "message": (
                            f"{criterion['title']} scored {criterion_value}, "
                            f"below threshold {finding_threshold}"
                        ),
                    }
                )

        capped = False
        if critical_zero and weighted_sum > critical_cap:
            weighted_sum = float(critical_cap)
            capped = True

        dimension_score = round(weighted_sum, dimension_rounding)
        dimension_results[dimension_id] = {
            "score": dimension_score,
            "applied_weight": 0.0,
            "capped": capped,
            "not_applicable": False,
            "criteria": criteria_output,
        }
        applicable_dimension_weights.append((dimension_id, dimension_def["weight"]))

    applied_dimension_weights = _redistribute_weights(applicable_dimension_weights)
    for dimension_id, applied_weight in applied_dimension_weights.items():
        dimension_results[dimension_id]["applied_weight"] = applied_weight

    composite_raw = sum(
        dimension_results[dimension_id]["score"] * applied_weight
        for dimension_id, applied_weight in applied_dimension_weights.items()
    )
    if composite_rounding == 0:
        composite_score = int(round(composite_raw))
    else:
        composite_score = round(composite_raw, composite_rounding)

    grade = _grade_for_score(int(composite_score), grades)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    return {
        "scoring_version": definition["version"],
        "composite_score": int(composite_score),
        "grade": grade,
        "dimensions": dimension_results,
        "findings": findings,
        "generated_at": generated_at,
    }
