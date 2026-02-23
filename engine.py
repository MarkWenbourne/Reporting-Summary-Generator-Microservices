from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


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

    # Normalize + sort (deterministic)
    norm: List[Dict[str, Any]] = []
    for a in assignments:
        if not isinstance(a, dict):
            continue
        course = str(a.get("course", "")).strip()
        title = str(a.get("title", "")).strip()
        due = str(a.get("dueDate", "")).strip()  # expected YYYY-MM-DD
        status = str(a.get("status", "")).strip() or "Not Started"
        norm.append({"course": course, "title": title, "dueDate": due, "status": status})

    # Filter out completed for "upcoming"
    upcoming = [a for a in norm if a["status"].lower() != "completed"]
    upcoming.sort(key=lambda x: (x["dueDate"], x["course"], x["title"]))

    shown = upcoming[:max_items]

    items: List[str] = []
    for a in shown:
        if include_details:
            items.append(f"{a['course']} — {a['title']} — Due {a['dueDate']} — Status: {a['status']}")
        else:
            items.append(f"{a['course']} — {a['title']} — Due {a['dueDate']}")

    # Highlights (deterministic, max 120 chars, at least 3 when possible)
    highlights: List[str] = []
    if shown:
        highlights.append(f"Next due: {shown[0]['course']} {shown[0]['title']} ({shown[0]['dueDate']})")
    highlights.append(f"{len(upcoming)} upcoming assignment(s) found")
    in_progress = sum(1 for a in upcoming if a["status"].lower() == "in progress")
    highlights.append(f"{in_progress} assignment(s) currently In Progress")

    # Ensure highlight length constraints (truncate safely)
    highlights = [_truncate(h, 120) for h in highlights]

    report = {
        "title": "Upcoming Deadlines Summary",
        "highlights": highlights,
        "sections": [
            {"header": "Upcoming Assignments", "items": items if items else ["(No upcoming assignments)"]}
        ],
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return report


def _generic_report(title: str, highlights: List[str], items: List[str]) -> Dict[str, Any]:
    return {
        "title": title,
        "highlights": [_truncate(h, 120) for h in highlights],
        "sections": [{"header": "Summary", "items": items}],
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def _truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"