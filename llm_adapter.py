# llm_adapter.py
import os
import openai
from typing import Dict, List
import json
import logging

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")  # use appropriate model
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

# Local HF fallback
use_local_generation = False
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    # small model example: "meta-llama/Llama-2-7b-chat" requires GPU and licensing; choose appropriate.
    # We won't automatically download a huge model. User can configure.
    local_pipe = None
except Exception as e:
    local_pipe = None

def call_openai_chat(system_prompt: str, user_prompt: str, temperature: float = 0.0) -> Dict:
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_API_KEY not set in env. Set or use local generation.")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    resp = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=900
    )
    return resp["choices"][0]["message"]["content"]

def call_local_model(prompt: str, max_new_tokens: int = 512) -> str:
    global local_pipe
    if local_pipe is None:
        # Lazy init - user must have set LOCAL_GENERATION_MODEL env var
        model_name = os.environ.get("LOCAL_GENERATION_MODEL")
        if not model_name:
            raise RuntimeError("No local model configured. Set LOCAL_GENERATION_MODEL env var or provide OPENAI_API_KEY.")
        # load model (this can be heavy)
        token = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
        local_pipe = pipeline("text-generation", model=model, tokenizer=token, max_length=2048)
    outputs = local_pipe(prompt, max_new_tokens=max_new_tokens, do_sample=False)
    return outputs[0]["generated_text"]

def call_llm_with_context(prompt: str, use_openai: bool = True, **kwargs) -> str:
    """
    Unified call. If OPENAI_API_KEY present and use_openai=True it'll call OpenAI, else local.
    """
    if use_openai and OPENAI_KEY:
        return call_openai_chat(kwargs.get("system_prompt","Legal clause assistant"), prompt, temperature=kwargs.get("temperature",0.0))
    else:
        return call_local_model(prompt, max_new_tokens=kwargs.get("max_new_tokens",512))
