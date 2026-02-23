from __future__ import annotations

from flask import Flask, jsonify, request

from engine import generate_report
from schemas import validate_request

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/report")
def report():
    payload = request.get_json(silent=True)
    ok, result = validate_request(payload)
    if not ok:
        return jsonify(result), 400

    report_type = result["reportType"]
    data = result["data"]
    options = result["options"]

    report_obj = generate_report(report_type, data, options)
    return jsonify(report_obj), 200


if __name__ == "__main__":
    # Local dev run
    app.run(host="127.0.0.1", port=5000, debug=True)