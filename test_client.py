import json
import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT_SECONDS = 2


def call_report(payload):
    resp = requests.post(f"{BASE_URL}/report", json=payload, timeout=TIMEOUT_SECONDS)
    print("\nStatus:", resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)


def main():
    # Valid request
    payload_ok = {
        "reportType": "deadlines",
        "data": {
            "studentName": "Mark",
            "assignments": [
                {"course": "CS 361", "title": "Assignment 7", "dueDate": "2026-02-23", "status": "In Progress"},
                {"course": "CS 381", "title": "HW5", "dueDate": "2026-02-25", "status": "Not Started"},
            ],
        },
        "options": {"maxItems": 10, "includeDetails": False},
    }

    # Invalid request (shows error handling)
    payload_bad = {"reportType": "gradesSnapshot", "data": {"x": 1}}

    print("=== Valid request ===")
    call_report(payload_ok)

    print("\n=== Invalid request ===")
    call_report(payload_bad)


if __name__ == "__main__":
    main()