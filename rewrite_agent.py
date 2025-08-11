# rewrite_agent.py
from retriever import retrieve
from llm_adapter import call_llm_with_context
import json
from typing import Dict, List

PROMPT_SYSTEM = """
You are a legal drafting assistant specialized in ADGM corporate documents. 
You will be given:
- an ORIGINAL_SNIPPET: a paragraph or clause from a client's uploaded document,
- a set of RELEVANT_SOURCES: numbered short text snippets with source references.
Your task:
1) Produce a concise, precise REWRITE of the ORIGINAL_SNIPPET that follows ADGM best practices,
2) Provide for each change a short RATIONALE,
3) Provide a CITATIONS block: list the sources you used (source id and a short quoted snippet no longer than 50 words),
4) Output strictly JSON with the following top-level keys:
   {
     "rewrite": "<the suggested clause text>",
     "rationale": "<2-3 sentence explanation>",
     "citations": [{"source": "<source_id>", "snippet": "<up-to-50-word snippet from source>"}],
     "confidence": "<Low|Medium|High>"
   }
If you cannot confidently rewrite, set "rewrite" to null and "confidence" to "Low".
Be concise and ensure the rewrite is legally clear and uses 'shall' for obligations rather than 'may' when appropriate.
"""

PROMPT_USER_TEMPLATE = """
ORIGINAL_SNIPPET:
\"\"\"{original}\
\"\"\"

RELEVANT_SOURCES:
{sources_list}

Instructions: produce the JSON described in the system message. Use only the provided RELEVANT_SOURCES for citations. Do not invent statutes; if no supporting source is present, say so and set confidence to Low.
"""

def format_sources_for_prompt(retrieved: List[Dict]) -> str:
    lines = []
    for i, r in enumerate(retrieved, start=1):
        lines.append(f"[{i}] source_id={r['chunk_id']} source={r['source']}\n{r['text']}\n")
    return "\n\n".join(lines)

def rewrite_clause(original_snippet: str, top_k: int = 5) -> Dict:
    # retrieve contexts
    retrieved = retrieve(original_snippet, k=top_k)
    sources_text = format_sources_for_prompt(retrieved)
    user_prompt = PROMPT_USER_TEMPLATE.format(original=original_snippet, sources_list=sources_text)
    raw = call_llm_with_context(user_prompt, use_openai=True, system_prompt=PROMPT_SYSTEM, temperature=0.0)
    # we expect the model to output JSON. Try to parse safely.
    try:
        j = json.loads(raw)
    except Exception:
        # fallback: try to extract JSON substring
        import re
        m = re.search(r"(\{[\s\S]*\})", raw)
        if m:
            j = json.loads(m.group(1))
        else:
            j = {"rewrite": None, "rationale": None, "citations": [], "confidence": "Low", "raw": raw}
    return {
        "original": original_snippet,
        "retrieved": retrieved,
        "llm_raw": raw,
        "result": j
    }
