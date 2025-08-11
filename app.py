# app.py
import gradio as gr
import json
import io
import os
import zipfile
from typing import List, Tuple

from parser import parse_uploaded_docx
from checker import find_issues_in_doc, verify_checklist
from annotator import insert_inline_comment_in_docx
from utils import ensure_dir

OUTPUT_DIR = "output"
ensure_dir(OUTPUT_DIR)


def _read_uploaded_file(f) -> Tuple[str, bytes]:
    """
    Accepts file-like objects (e.g. Gradio upload) or raw bytes.
    Returns (filename, bytes).
    """
    if hasattr(f, "read"):
        data = f.read()
        name = getattr(f, "name", getattr(f, "filename", "uploaded.docx"))
    else:
        # raw bytes passed directly
        data = f
        name = "uploaded.docx"
    return name, data


def process_files(files: List):
    """
    Main orchestrator.
    files: list of file-like objects where file.read() returns bytes and file.name exists.
    Returns (report_json_str, path_to_zip)
    """
    parsed = []
    uploaded_types = []
    raw_texts = {}

    # normalize and parse uploads
    for f in files:
        name, b = _read_uploaded_file(f)
        # ensure bytes
        if isinstance(b, str):
            b = b.encode("utf-8")
        p = parse_uploaded_docx(b)
        p["filename"] = name
        parsed.append((name, b, p))
        uploaded_types.append(p["doc_type"])
        raw_texts[name] = p["text"]

    # process detection / checklist
    process_info = verify_checklist(uploaded_types, process="Company Incorporation")

    issues_summary = []
    annotated_files = []

    # lazy import so tests can monkeypatch rewrite_agent before import if needed
    from rewrite_agent import rewrite_clause

    for (name, bytes_, parsed_meta) in parsed:
        text = parsed_meta["text"]
        issues = find_issues_in_doc(text)

        # perform rewrites for medium+ severity
        for issue in issues:
            if issue.get("severity", "Low") in ["High", "Medium"]:
                anchor = issue.get("details", "")
                # get a sensible snippet: try to pick the sentence containing anchor, else front chunk
                snippet = None
                if anchor and len(anchor) > 20:
                    snippet = anchor
                else:
                    snippet = text[:400]
                try:
                    rewrite_out = rewrite_clause(snippet, top_k=6)
                except Exception as e:
                    # if LLM or retriever fails, attach a failure note but continue
                    issue["rewrite_error"] = str(e)
                    issue["suggested_rewrite"] = None
                    issue["rewrite_rationale"] = None
                    issue["rewrite_confidence"] = "Low"
                    issue["rewrite_citations"] = []
                else:
                    # rewrite_out expected to be dict with key "result" as in earlier design
                    res = rewrite_out.get("result") if isinstance(rewrite_out, dict) else None
                    if isinstance(res, dict):
                        issue["suggested_rewrite"] = res.get("rewrite")
                        issue["rewrite_rationale"] = res.get("rationale")
                        issue["rewrite_confidence"] = res.get("confidence")
                        issue["rewrite_citations"] = res.get("citations", [])
                    else:
                        # fallback if rewrite_out already contains top-level JSON
                        issue["suggested_rewrite"] = rewrite_out.get("rewrite") if isinstance(rewrite_out, dict) else None
                        issue["rewrite_rationale"] = rewrite_out.get("rationale") if isinstance(rewrite_out, dict) else None
                        issue["rewrite_confidence"] = rewrite_out.get("confidence") if isinstance(rewrite_out, dict) else "Low"
                        issue["rewrite_citations"] = rewrite_out.get("citations", []) if isinstance(rewrite_out, dict) else []

        # annotate docx with issues (which may now include suggested_rewrite)
        annotated_bytes = insert_inline_comment_in_docx(bytes_, issues, text)
        reviewed_name = name.replace(".docx", "_reviewed.docx")
        annotated_files.append((reviewed_name, annotated_bytes))

        issues_summary.append({
            "document": name,
            "doc_type": parsed_meta["doc_type"],
            "doc_confidence": parsed_meta["doc_confidence"],
            "issues": issues
        })

    # prepare JSON report
    report = {
        "process_check": process_info,
        "documents_analyzed": len(parsed),
        "issues_found": issues_summary
    }

    # save outputs to zip
    zip_path = os.path.join(OUTPUT_DIR, "results.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        # add reviewed docs
        for fname, data in annotated_files:
            zf.writestr(fname, data)
        zf.writestr("report.json", json.dumps(report, indent=2))

    return json.dumps(report, indent=2), zip_path


# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("# ADGM Corporate Agent — Document Review (Demo)")
    with gr.Row():
        doc_input = gr.File(label="Upload your .docx files (multiple allowed)", file_count="multiple", file_types=[".docx"])
    run_btn = gr.Button("Run Review")
    output_text = gr.JSON(label="Structured JSON Report")
    result_zip = gr.File(label="Download results zip")

    def run_and_return(files):
        report_str, zip_path = process_files(files)
        return json.loads(report_str), zip_path

    run_btn.click(run_and_return, inputs=[doc_input], outputs=[output_text, result_zip])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False)
