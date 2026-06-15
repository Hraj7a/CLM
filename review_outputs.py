import json
import csv
from pathlib import Path


OUTPUTS_FOLDER = Path("outputs")
REVIEW_FILE = OUTPUTS_FOLDER / "extraction_review.csv"


def get_nested(data, *keys):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def is_found(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in ["", "Not found", "not found", "غير موجود"]
    return True


def main():
    json_files = sorted(OUTPUTS_FOLDER.glob("*_extraction.json"))

    if not json_files:
        print("No extraction JSON files found in outputs folder.")
        return

    rows = []

    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            title = get_nested(data, "contract_title", "value")
            parties = data.get("contracting_parties", [])
            effective_date = get_nested(data, "effective_date", "value")
            expiration_date = get_nested(data, "expiration_date", "value")
            governing_law = get_nested(data, "governing_law", "value")
            jurisdiction = get_nested(data, "jurisdiction", "value")
            payment_summary = get_nested(data, "payment_terms", "summary")
            obligations = data.get("key_obligations", [])
            deliverables = data.get("deliverables", [])
            missing_info = data.get("missing_information", [])
            unclear_clauses = data.get("unclear_clauses", [])

            rows.append({
                "file": file_path.name,
                "json_valid": "Yes",
                "title_found": "Yes" if is_found(title) else "No",
                "parties_count": len(parties) if isinstance(parties, list) else 0,
                "effective_date_found": "Yes" if is_found(effective_date) else "No",
                "expiration_date_found": "Yes" if is_found(expiration_date) else "No",
                "governing_law_found": "Yes" if is_found(governing_law) else "No",
                "jurisdiction_found": "Yes" if is_found(jurisdiction) else "No",
                "payment_terms_found": "Yes" if is_found(payment_summary) else "No",
                "obligations_count": len(obligations) if isinstance(obligations, list) else 0,
                "deliverables_count": len(deliverables) if isinstance(deliverables, list) else 0,
                "missing_info_count": len(missing_info) if isinstance(missing_info, list) else 0,
                "unclear_clauses_count": len(unclear_clauses) if isinstance(unclear_clauses, list) else 0,
                "error": ""
            })

        except Exception as e:
            rows.append({
                "file": file_path.name,
                "json_valid": "No",
                "title_found": "No",
                "parties_count": 0,
                "effective_date_found": "No",
                "expiration_date_found": "No",
                "governing_law_found": "No",
                "jurisdiction_found": "No",
                "payment_terms_found": "No",
                "obligations_count": 0,
                "deliverables_count": 0,
                "missing_info_count": 0,
                "unclear_clauses_count": 0,
                "error": str(e)
            })

    with open(REVIEW_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Review file created: {REVIEW_FILE}")


if __name__ == "__main__":
    main()