# checker.py
import re
from typing import List, Dict, Tuple

# Example checklist for Company Incorporation (from Task.pdf)
INCORPORATION_CHECKLIST = [
    "Articles of Association (AoA)",
    "Memorandum of Association (MoA/MoU)",
    "Board Resolution Templates",
    "Shareholder Resolution Templates",
    "Register of Members and Directors",
    "Incorporation Application Form",
    "UBO Declaration Form",
]

# Red-flag detectors: returns list of issues
def detect_jurisdiction_issue(text: str) -> List[Dict]:
    issues = []
    # If document references 'UAE Federal Courts' or 'Dubai Courts' or 'non-ADGM' keywords
    matches = re.findall(r"\b(uae federal courts|federal courts|dubai courts|abu dhabi courts)\b", text.lower())
    if matches:
        issues.append({
            "issue": "Incorrect jurisdiction reference",
            "severity": "High",
            "details": f"Found references: {list(set(matches))}",
            "recommendation": "Use ADGM jurisdiction language (e.g., 'Courts of the Abu Dhabi Global Market (ADGM)')"
        })
    return issues

def detect_missing_signatory(text: str) -> List[Dict]:
    issues = []
    # Simple heuristic: look for 'Signed by' or 'Signature' or 'For and on behalf' near end
    if not re.search(r"\b(signed by|signature|for and on behalf|authorized signatory)\b", text.lower()):
        issues.append({
            "issue": "Missing signatory section",
            "severity": "Medium",
            "details": "No typical signatory phrases found.",
            "recommendation": "Add signatory block with name, title, date, and witness if required by ADGM guidelines."
        })
    return issues

def detect_ambiguous_language(text: str) -> List[Dict]:
    issues = []
    # look for 'may' used in critical clauses where 'shall' is expected
    ambiguous_matches = re.findall(r"\bmay\b", text.lower())
    if ambiguous_matches and len(ambiguous_matches) > 2:  # threshold
        issues.append({
            "issue": "Excessive ambiguous modal verbs (may/can)",
            "severity": "Low",
            "details": f"Count of 'may' or similar: {len(ambiguous_matches)}",
            "recommendation": "Consider replacing 'may' with 'shall' or clearer obligations where legal certainty required."
        })
    return issues

def find_issues_in_doc(text: str) -> List[Dict]:
    issues = []
    issues.extend(detect_jurisdiction_issue(text))
    issues.extend(detect_missing_signatory(text))
    issues.extend(detect_ambiguous_language(text))
    # Add more detectors as needed (missing clause patterns, UBO mentions, etc.)
    return issues

def verify_checklist(uploaded_types: List[str], process: str = "Company Incorporation") -> Dict:
    # For now only support incorporation process
    required = INCORPORATION_CHECKLIST
    present = []
    missing = []
    for r in required:
        # simple mapping: check if any uploaded_types contains keywords of r
        found = any(r.split()[0].lower() in (t.lower()) for t in uploaded_types)
        if found:
            present.append(r)
        else:
            missing.append(r)
    return {
        "process": process,
        "required_documents": len(required),
        "documents_uploaded": len(uploaded_types),
        "missing_documents": missing,
        "present_documents": present
    }
