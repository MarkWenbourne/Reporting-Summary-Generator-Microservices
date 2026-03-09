from __future__ import annotations
from typing import Any, Dict, List, Tuple


SUPPORTED_REPORT_TYPES = {"deadlines", "portfolio", "iotStatus", "gameRunSummary"}


def validate_request(payload: Any) -> Tuple[bool, Dict[str, Any]]:
    """
    Returns (is_valid, result)
    - if is_valid=True: result contains normalized payload
    - if is_valid=False: result contains error response body
    """

    ok, result = _validate_payload_structure(payload)
    if not ok:
        return False, result

    report_type, data, options = result

    ok, err = _validate_report_type(report_type)
    if not ok:
        return False, err

    ok, err = _validate_data_and_options(data, options)
    if not ok:
        return False, err

    ok, err = _validate_report_specific(report_type, data)
    if not ok:
        return False, err

    normalized = _normalize_request(report_type, data, options)
    return True, normalized


def _validate_payload_structure(payload: Any) -> Tuple[bool, Any]:
    if not isinstance(payload, dict):
        return False, error(
            message="Request body must be a JSON object.",
            details={"expected": "object", "got": type(payload).__name__},
        )

    report_type = payload.get("reportType")
    data = payload.get("data")
    options = payload.get("options", {})

    return True, (report_type, data, options)


def _validate_report_type(report_type: Any) -> Tuple[bool, Dict[str, Any]]:
    if not isinstance(report_type, str) or not report_type.strip():
        return False, error(
            message="Missing or invalid 'reportType' (must be a non-empty string).",
            details={"field": "reportType"},
        )

    if report_type not in SUPPORTED_REPORT_TYPES:
        return False, error(
            message=f"Unsupported reportType: '{report_type}'. Supported types: {', '.join(sorted(SUPPORTED_REPORT_TYPES))}.",
            details={"reportType": report_type},
        )

    return True, {}


def _validate_data_and_options(data: Any, options: Any) -> Tuple[bool, Dict[str, Any]]:
    if not isinstance(data, dict):
        return False, error(
            message="Missing or invalid 'data' (must be a JSON object).",
            details={"field": "data"},
        )

    if not isinstance(options, dict):
        return False, error(
            message="Invalid 'options' (must be a JSON object if provided).",
            details={"field": "options"},
        )

    return True, {}


def _validate_report_specific(report_type: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    missing: List[str] = []

    if report_type == "deadlines":
        if "assignments" not in data:
            missing.append("data.assignments")
        elif not isinstance(data["assignments"], list):
            return False, error(
                message="data.assignments must be a list.",
                details={"field": "data.assignments"},
            )

    if missing:
        return False, error(
            message="Missing required fields for reportType.",
            details={"missing": missing, "reportType": report_type},
        )

    return True, {}


def _normalize_request(report_type: str, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "reportType": report_type,
        "data": data,
        "options": options,
    }


def error(message: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "errorCode": "INVALID_REQUEST",
        "message": message,
    }
    if details:
        body["details"] = details
    return body
