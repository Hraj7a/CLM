import json
import csv
from pathlib import Path


# -----------------------------
# Folders
# -----------------------------
OUTPUTS_FOLDER = Path("outputs")
RISK_FOLDER = OUTPUTS_FOLDER / "risk_analysis"
COMBINED_FOLDER = OUTPUTS_FOLDER / "combined_reports"


# -----------------------------
# Helper functions
# -----------------------------
def read_json(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(file_path: Path, data: dict):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_value(data: dict, key: str, subkey: str = "value"):
    item = data.get(key, {})
    if isinstance(item, dict):
        return item.get(subkey, "")
    return ""


def detect_language(text: str) -> str:
    arabic_chars = sum(1 for char in text if "\u0600" <= char <= "\u06FF")
    return "Arabic" if arabic_chars > 0 else "English"


def get_top_risks(risk_data: dict, limit: int = 5):
    risks = risk_data.get("risks", [])
    if not isinstance(risks, list):
        return []

    level_priority = {
        "High": 3,
        "Medium": 2,
        "Low": 1
    }

    sorted_risks = sorted(
        risks,
        key=lambda r: level_priority.get(r.get("risk_level", ""), 0),
        reverse=True
    )

    top_risks = []

    for risk in sorted_risks[:limit]:
        top_risks.append({
            "risk_title": risk.get("risk_title", ""),
            "risk_level": risk.get("risk_level", ""),
            "risk_category": risk.get("risk_category", ""),
            "recommendation": risk.get("recommendation", "")
        })

    return top_risks


def build_combined_report(extraction_file: Path, risk_file: Path) -> dict:
    extraction_data = read_json(extraction_file)
    risk_data = read_json(risk_file)

    contract_title = get_value(extraction_data, "contract_title")
    governing_law = get_value(extraction_data, "governing_law")
    jurisdiction = get_value(extraction_data, "jurisdiction")
    effective_date = get_value(extraction_data, "effective_date")
    expiration_date = get_value(extraction_data, "expiration_date")

    parties = extraction_data.get("contracting_parties", [])
    missing_information = extraction_data.get("missing_information", [])
    missing_clauses = risk_data.get("missing_clauses", [])

    language = detect_language(
        json.dumps(extraction_data, ensure_ascii=False)
    )

    combined_report = {
        "source_files": {
            "extraction_file": extraction_file.name,
            "risk_analysis_file": risk_file.name
        },
        "contract_name": extraction_file.name.replace("_extraction.json", ""),
        "language": language,
        "dashboard_summary": {
            "contract_title": contract_title,
            "overall_risk_level": risk_data.get("overall_risk_level", ""),
            "risk_score": risk_data.get("risk_score", ""),
            "risk_summary": risk_data.get("risk_summary", ""),
            "parties_count": len(parties) if isinstance(parties, list) else 0,
            "effective_date": effective_date,
            "expiration_date": expiration_date,
            "governing_law": governing_law,
            "jurisdiction": jurisdiction,
            "top_risks": get_top_risks(risk_data, limit=5),
            "missing_information_count": len(missing_information) if isinstance(missing_information, list) else 0,
            "missing_clauses_count": len(missing_clauses) if isinstance(missing_clauses, list) else 0,
            "human_review_required": risk_data.get("human_review_required", True)
        },
        "extraction": extraction_data,
        "risk_analysis": risk_data
    }

    return combined_report


def main():
    COMBINED_FOLDER.mkdir(exist_ok=True)

    extraction_files = sorted(OUTPUTS_FOLDER.glob("*_extraction.json"))

    if not extraction_files:
        print("No extraction JSON files found.")
        return

    dashboard_rows = []

    for extraction_file in extraction_files:
        risk_file_name = extraction_file.name.replace(
            "_extraction.json",
            "_risk_analysis.json"
        )

        risk_file = RISK_FOLDER / risk_file_name

        if not risk_file.exists():
            print(f"Risk file missing for: {extraction_file.name}")
            continue

        combined_report = build_combined_report(extraction_file, risk_file)

        combined_file_name = extraction_file.name.replace(
            "_extraction.json",
            "_combined_report.json"
        )

        combined_file = COMBINED_FOLDER / combined_file_name
        write_json(combined_file, combined_report)

        summary = combined_report["dashboard_summary"]

        dashboard_rows.append({
            "contract_name": combined_report["contract_name"],
            "language": combined_report["language"],
            "contract_title": summary["contract_title"],
            "overall_risk_level": summary["overall_risk_level"],
            "risk_score": summary["risk_score"],
            "parties_count": summary["parties_count"],
            "effective_date": summary["effective_date"],
            "expiration_date": summary["expiration_date"],
            "governing_law": summary["governing_law"],
            "jurisdiction": summary["jurisdiction"],
            "missing_information_count": summary["missing_information_count"],
            "missing_clauses_count": summary["missing_clauses_count"],
            "human_review_required": summary["human_review_required"],
            "combined_report_file": combined_file.name
        })

        print(f"Created: {combined_file}")

    dashboard_csv = COMBINED_FOLDER / "dashboard_summary.csv"

    with open(dashboard_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "contract_name",
                "language",
                "contract_title",
                "overall_risk_level",
                "risk_score",
                "parties_count",
                "effective_date",
                "expiration_date",
                "governing_law",
                "jurisdiction",
                "missing_information_count",
                "missing_clauses_count",
                "human_review_required",
                "combined_report_file"
            ]
        )
        writer.writeheader()
        writer.writerows(dashboard_rows)

    print("\nCombined reports finished.")
    print(f"Dashboard summary saved to: {dashboard_csv}")


if __name__ == "__main__":
    main()