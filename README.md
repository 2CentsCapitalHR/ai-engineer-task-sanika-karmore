[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/vgbm4cZ0)

# ADGM-Compliant Corporate Agent with Document Intelligence

## Task Overview
The Corporate Agent is an intelligent AI-powered legal assistant designed to assist users in reviewing, validating, and preparing documentation for business incorporation and compliance within the Abu Dhabi Global Market (ADGM) jurisdiction.

### Key Capabilities:
1. Accept `.docx` documents uploaded by users.
2. Verify completeness of submissions based on ADGM rules.
3. Highlight red flags and inconsistencies in documents.
4. Insert contextual comments into `.docx` files.
5. Generate a reviewed, downloadable version of the file.
6. Notify users of missing mandatory documents based on a pre-defined checklist.
7. Apply Retrieval-Augmented Generation (RAG) for legal accuracy using ADGM references.

---

## Functional Objectives
The Corporate Agent achieves the following:
1. Accepts `.docx` documents uploaded by users.
2. Parses uploaded documents and identifies document types.
3. Checks if all mandatory documents are present for specific legal processes (e.g., company incorporation).
4. Detects legal red flags and inconsistencies within each document.
5. Inserts contextual comments in `.docx` files for flagged content.
6. Outputs a downloadable marked-up `.docx` file.
7. Generates a structured JSON report summarizing findings.

---

## Features

### Document Checklist Verification
- Automatically recognizes the legal process (e.g., incorporation, licensing).
- Compares uploaded documents against the ADGM checklist.
- Notifies users of missing mandatory documents.

Example:
> "It appears that you’re trying to incorporate a company in ADGM. Based on our reference list, you have uploaded 4 out of 5 required documents. The missing document appears to be: ‘Register of Members and Directors’."

---

### Red Flag Detection
The agent detects:
- Invalid or missing clauses.
- Incorrect jurisdiction references (e.g., UAE Federal Courts instead of ADGM).
- Ambiguous or non-binding language.
- Missing signatory sections or improper formatting.
- Non-compliance with ADGM-specific templates.

---

### Inline Commenting
- Inserts comments inside `.docx` files at relevant locations.
- Cites applicable ADGM laws or rules (e.g., “Per ADGM Companies Regulations 2020, Art. 6...”).
- (Optional) Offers alternative clause wording for common issues.

---

## Document Types and Use Cases
### Company Formation Documents:
- Articles of Association (AoA)
- Memorandum of Association (MoA/MoU)
- Incorporation Application Form
- UBO Declaration Form
- Board Resolution Templates
- Register of Members and Directors
- Shareholder Resolution Templates
- Change of Registered Address Notice

### Other Categories:
- Licensing Regulatory Filings
- Employment HR Contracts
- Commercial Agreements
- Compliance Risk Policies

---

## Output Format
The agent generates:
1. A reviewed `.docx` file with highlights/comments.
2. A structured JSON report summarizing the analysis.

Example JSON:
```json
{
  "process": "Company Incorporation",
  "documents_uploaded": 4,
  "required_documents": 5,
  "missing_document": "Register of Members and Directors",
  "issues_found": [
    {
      "document": "Articles of Association",
      "section": "Clause 3.1",
      "issue": "Jurisdiction clause does not specify ADGM",
      "severity": "High",
      "suggestion": "Update jurisdiction to ADGM Courts."
    }
  ]
}
