import json
import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DATA_FILE = Path(__file__).with_name("rules.json")

with DATA_FILE.open("r", encoding="utf-8") as file:
    DATABASE = json.load(file)

SAFETY_NOTICE = (
    "This is a student prototype using fictional records. A demo match is not a real-world "
    "product approval or a recommendation to apply a treatment. For actual crop treatment, "
    "check current official product labels and consult a qualified agricultural professional."
)


def normalize(value):
    """Normalize user-entered text for simple exact comparisons."""
    return str(value or "").strip().lower()


def verify_treatment(payload):
    crop = normalize(payload.get("crop"))
    stage = normalize(payload.get("growth_stage"))
    problem = normalize(payload.get("target_problem"))
    product_id = normalize(payload.get("product_id"))
    requested_reference = normalize(payload.get("reference_id"))

    checks = []
    record = next(
        (item for item in DATABASE["records"]
         if normalize(item["product_id"]) == product_id),
        None
    )

    if not crop or not stage or not problem or not product_id:
        return {
            "status": "insufficient_evidence",
            "summary": "Required information is missing. Complete the crop, stage, suspected problem, and demo product fields.",
            "checks": [{
                "name": "Required fields",
                "passed": None,
                "detail": "Crop, growth stage, suspected problem, and product ID are required."
            }],
            "reference": None,
            "safety_notice": SAFETY_NOTICE
        }

    if record is None:
        return {
            "status": "insufficient_evidence",
            "summary": "The product ID is not present in the fictional demo database. The system cannot verify this proposal.",
            "checks": [{
                "name": "Reference lookup",
                "passed": None,
                "detail": "No matching demo record exists. No conclusion about a real product can be drawn."
            }],
            "reference": None,
            "safety_notice": SAFETY_NOTICE
        }

    reference = DATABASE["references"].get(record["reference_id"])
    if requested_reference and requested_reference != normalize(record["reference_id"]):
        checks.append({
            "name": "Reference ID",
            "passed": False,
            "detail": "The entered reference ID does not match the reference linked to this demo record."
        })
    else:
        checks.append({
            "name": "Reference ID",
            "passed": True if not requested_reference else True,
            "detail": "The reference ID matches the demo record." if requested_reference else
                      "The linked demo reference was retrieved automatically."
        })

    mismatch = False
    unknown = False

    expected_crop = normalize(record.get("crop"))
    if crop != expected_crop:
        mismatch = True
        checks.append({
            "name": "Crop match",
            "passed": False,
            "detail": f"The demo record is for '{record.get('crop')}', but the submitted crop is '{crop}'."
        })
    else:
        checks.append({
            "name": "Crop match", "passed": True,
            "detail": "The submitted crop matches the crop named in the fictional record."
        })

    expected_problem = normalize(record.get("target_problem"))
    if problem == "unknown":
        unknown = True
        checks.append({
            "name": "Target problem",
            "passed": None,
            "detail": "The suspected problem is unknown, so a target-problem comparison cannot be completed."
        })
    elif problem != expected_problem:
        mismatch = True
        checks.append({
            "name": "Target problem",
            "passed": False,
            "detail": f"The demo record is tagged '{record.get('target_problem_label')}', which differs from the submitted problem."
        })
    else:
        checks.append({
            "name": "Target problem", "passed": True,
            "detail": "The submitted problem matches the label in the fictional record; this is not a diagnosis."
        })

    allowed_stages = [normalize(item) for item in record.get("example_stages", [])]
    if stage == "unknown":
        unknown = True
        checks.append({
            "name": "Growth stage",
            "passed": None,
            "detail": "The growth stage is unknown; this check cannot be completed."
        })
    elif stage not in allowed_stages:
        mismatch = True
        checks.append({
            "name": "Growth stage",
            "passed": False,
            "detail": "The submitted stage is not listed in this fictional test record."
        })
    else:
        checks.append({
            "name": "Growth stage", "passed": True,
            "detail": "The stage matches the example record's test condition only."
        })

    if requested_reference and requested_reference != normalize(record["reference_id"]):
        mismatch = True

    if mismatch:
        status = "mismatch"
        summary = "At least one submitted field conflicts with this fictional test record. The system has not assessed any real product's suitability."
    elif unknown:
        status = "insufficient_evidence"
        summary = "The known fields did not reveal a mismatch, but at least one required detail is unknown. The proposal cannot be verified."
    else:
        status = "match"
        summary = "All submitted fields match this fictional test record. This demonstrates matching logic only; it is not evidence of real product approval, treatment safety, or treatment necessity."

    return {
        "status": status,
        "summary": summary,
        "checks": checks,
        "reference": {
            "id": reference["id"],
            "title": reference["title"],
            "source": reference["source"],
            "note": reference["note"]
        } if reference else None,
        "safety_notice": SAFETY_NOTICE
    }


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "AgroGuard AI demo API"})


@app.get("/api/records")
def records():
    """Expose only the fictional sample IDs for the frontend demo."""
    return jsonify({
        "notice": "Fictional demonstration records only; not real agricultural recommendations.",
        "records": [
            {
                "product_id": item["product_id"],
                "target_problem_label": item["target_problem_label"],
                "example_stages": item["example_stages"]
            }
            for item in DATABASE["records"]
        ]
    })


@app.post("/api/verify")
def verify():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Send a JSON object with the form fields."}), 400
    return jsonify(verify_treatment(payload))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
