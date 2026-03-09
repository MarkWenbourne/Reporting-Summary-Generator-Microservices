from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def generate_report(report_type: str, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic report generation.
    Returns a JSON-serializable dict with:
      title, highlights, sections, generatedAt
    """
    if report_type == "deadlines":
        return _deadlines_report(data, options)

    # Stubs for other types (still valid responses)
    if report_type == "portfolio":
        return _generic_report("Portfolio Summary", ["Portfolio report type not yet expanded."], ["(No items)"])
    if report_type == "iotStatus":
        return _generic_report("IoT Status Summary", ["IoT report type not yet expanded."], ["(No items)"])
    if report_type == "gameRunSummary":
        return _generic_report("Game Run Summary", ["Game report type not yet expanded."], ["(No items)"])

    # Should not happen if schemas validate
    return _generic_report("Unknown Report", ["Unsupported type."], ["(No items)"])


def _deadlines_report(data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
    assignments = data.get("assignments", [])
    max_items = int(options.get("maxItems", 10))
    include_details = bool(options.get("includeDetails", False))

    normalized = _normalize_assignments(assignments)
    upcoming = _get_upcoming_assignments(normalized)
    shown = upcoming[:max_items]

    items = _build_deadline_items(shown, include_details)
    highlights = _build_deadline_highlights(shown, upcoming)

    return {
        "title": "Upcoming Deadlines Summary",
        "highlights": highlights,
        "sections": [
            {
                "header": "Upcoming Assignments",
                "items": items if items else ["(No upcoming assignments)"],
            }
        ],
        "generatedAt": _utc_now_str(),
    }


def _normalize_assignments(assignments: List[Any]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []

    for assignment in assignments:
        if not isinstance(assignment, dict):
            continue

        course = str(assignment.get("course", "")).strip()
        title = str(assignment.get("title", "")).strip()
        due_date = str(assignment.get("dueDate", "")).strip()  # expected YYYY-MM-DD
        status = str(assignment.get("status", "")).strip() or "Not Started"

        normalized.append(
            {
                "course": course,
                "title": title,
                "dueDate": due_date,
                "status": status,
            }
        )

    return normalized


def _get_upcoming_assignments(assignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    upcoming = [assignment for assignment in assignments if assignment["status"].lower() != "completed"]
    upcoming.sort(key=lambda item: (item["dueDate"], item["course"], item["title"]))
    return upcoming


def _build_deadline_items(assignments: List[Dict[str, Any]], include_details: bool) -> List[str]:
    items: List[str] = []

    for assignment in assignments:
        if include_details:
            items.append(
                f"{assignment['course']} — {assignment['title']} — Due {assignment['dueDate']} — Status: {assignment['status']}"
            )
        else:
            items.append(f"{assignment['course']} — {assignment['title']} — Due {assignment['dueDate']}")

    return items


def _build_deadline_highlights(shown: List[Dict[str, Any]], upcoming: List[Dict[str, Any]]) -> List[str]:
    highlights: List[str] = []

    if shown:
        highlights.append(f"Next due: {shown[0]['course']} {shown[0]['title']} ({shown[0]['dueDate']})")

    highlights.append(f"{len(upcoming)} upcoming assignment(s) found")

    in_progress = sum(1 for assignment in upcoming if assignment["status"].lower() == "in progress")
    highlights.append(f"{in_progress} assignment(s) currently In Progress")

    return [_truncate(highlight, 120) for highlight in highlights]


def _generic_report(title: str, highlights: List[str], items: List[str]) -> Dict[str, Any]:
    return {
        "title": title,
        "highlights": [_truncate(h, 120) for h in highlights],
        "sections": [{"header": "Summary", "items": items}],
        "generatedAt": _utc_now_str(),
    }


def _utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"
