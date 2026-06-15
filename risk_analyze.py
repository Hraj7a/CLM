import os
import json
import csv
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# -----------------------------
# Settings
# -----------------------------
OUTPUTS_FOLDER = Path("outputs")
RISK_OUTPUTS_FOLDER = OUTPUTS_FOLDER / "risk_analysis"

# Start with 2 for testing.
# After it works, change this to None.
TEST_LIMIT = None


# -----------------------------
# Risk Analysis Prompt
# -----------------------------
SYSTEM_PROMPT = """
You are an AI contract risk analysis assistant.

Your task is to analyze extracted contract data and identify legal, commercial, operational, and compliance risks.

Important rules:
- Do not invent facts.
- Base your analysis only on the provided extracted contract data.
- If information is missing, treat that as a possible risk.
- Do not provide final legal advice. Provide review points for a legal or compliance professional.
- Use clear and concise language.
- Use the same language as the extracted contract where appropriate.
- The output must be valid JSON only.

Risk categories to consider:
- Missing critical clauses
- Governing law and jurisdiction
- Payment and financial risk
- Termination risk
- Liability and indemnity risk
- Confidentiality risk
- Data protection / privacy risk
- Ambiguous obligations
- Renewal and expiry risk
- Operational compliance risk

Return this JSON structure:

{
  "contract_title": "",
  "overall_risk_level": "Low / Medium / High",
  "risk_score": 0,
  "risk_summary": "",
  "risks": [
    {
      "risk_title": "",
      "risk_level": "Low / Medium / High",
      "risk_category": "",
      "explanation": "",
      "evidence": "",
      "recommendation": ""
    }
  ],
  "missing_clauses": [
    {
      "clause_name": "",
      "risk_level": "Low / Medium / High",
      "why_it_matters": "",
      "recommendation": ""
    }
  ],
  "recommended_actions": [],
  "human_review_required": true
}

Scoring guide:
- 0 to 30 = Low risk
- 31 to 70 = Medium risk
- 71 to 100 = High risk
"""


# -----------------------------
# Load environment
# -----------------------------
load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not endpoint or not api_key or not deployment:
    raise ValueError(
        "Missing .env values. Check AZURE_OPENAI_ENDPOINT, "
        "AZURE_OPENAI_API_KEY, and AZURE_OPENAI_DEPLOYMENT."
    )

client = OpenAI(
    api_key=api_key,
    base_url=f"{endpoint.rstrip('/')}/openai/v1/"
)


# -----------------------------
# Helper functions
# -----------------------------
def analyze_risk(extraction_data: dict) -> dict:
    """Send extracted contract JSON to Azure OpenAI and return risk analysis JSON."""

    response = client.chat.completions.create(
        model=deployment,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    "Analyze the following extracted contract data for risks:\n\n"
                    + json.dumps(extraction_data, ensure_ascii=False, indent=2)
                )
            }
        ]
    )

    content = response.choices[0].message.content
    return json.loads(content)


def main():
    RISK_OUTPUTS_FOLDER.mkdir(exist_ok=True)

    extraction_files = sorted(OUTPUTS_FOLDER.glob("*_extraction.json"))

    if not extraction_files:
        print("No extraction JSON files found in outputs folder.")
        return

    if TEST_LIMIT is not None:
        extraction_files = extraction_files[:TEST_LIMIT]

    summary_rows = []

    for index, file_path in enumerate(extraction_files, start=1):
        print(f"[{index}/{len(extraction_files)}] Analyzing risks: {file_path.name}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                extraction_data = json.load(f)

            risk_data = analyze_risk(extraction_data)

            output_name = file_path.name.replace("_extraction.json", "_risk_analysis.json")
            output_file = RISK_OUTPUTS_FOLDER / output_name

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(risk_data, f, ensure_ascii=False, indent=2)

            risks = risk_data.get("risks", [])
            missing_clauses = risk_data.get("missing_clauses", [])

            summary_rows.append({
                "file": file_path.name,
                "status": "success",
                "overall_risk_level": risk_data.get("overall_risk_level", ""),
                "risk_score": risk_data.get("risk_score", ""),
                "risks_count": len(risks) if isinstance(risks, list) else 0,
                "missing_clauses_count": len(missing_clauses) if isinstance(missing_clauses, list) else 0,
                "output": output_file.name,
                "error": ""
            })

            print(f"Saved: {output_file}")

            time.sleep(1)

        except Exception as e:
            summary_rows.append({
                "file": file_path.name,
                "status": "failed",
                "overall_risk_level": "",
                "risk_score": "",
                "risks_count": 0,
                "missing_clauses_count": 0,
                "output": "",
                "error": str(e)
            })

            print(f"Failed: {file_path.name}")
            print(f"Error: {e}")

    summary_file = RISK_OUTPUTS_FOLDER / "risk_summary.csv"

    with open(summary_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file",
                "status",
                "overall_risk_level",
                "risk_score",
                "risks_count",
                "missing_clauses_count",
                "output",
                "error"
            ]
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    print("\nRisk analysis finished.")
    print(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()