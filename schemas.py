from __future__ import annotations
from typing import Any, Dict, List, Tuple


SUPPORTED_REPORT_TYPES = {"deadlines", "portfolio", "iotStatus", "gameRunSummary"}


def validate_request(payload: Any) -> Tuple[bool, Dict[str, Any]]:
    """
    Returns (ok, result)
    - if ok=True: result contains normalized payload
    - if ok=False: result contains error response body
    """
    if not isinstance(payload, dict):
        return False, error(
            message="Request body must be a JSON object.",
            details={"expected": "object", "got": type(payload).__name__},
        )

    report_type = payload.get("reportType")
    data = payload.get("data")
    options = payload.get("options", {})

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

    # Report-type specific checks (lightweight, but useful)
    missing: List[str] = []
    if report_type == "deadlines":
        # expects: assignments list
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

    normalized = {"reportType": report_type, "data": data, "options": options}
    return True, normalized


def error(message: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "errorCode": "INVALID_REQUEST",
        "message": message,
    }
    if details:
        body["details"] = details
    return body