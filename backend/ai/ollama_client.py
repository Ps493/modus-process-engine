import json
import re
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from ai.llm_client import LLMClient, build_prompt


def _extract_json(text: str) -> dict:
    """Local models don't always respect 'JSON only' - strip fences / leading text."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


class OllamaClient(LLMClient):
    def __init__(self):
        self._base_url = settings.ollama_base_url
        self._model = settings.ollama_model

    def is_available(self) -> bool:
        try:
            r = httpx.get(f"{self._base_url}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
    def analyze_process(self, process_name: str, business_purpose_raw: str,
                         category: Optional[str], evidence_chunks: list[str]) -> dict:
        prompt = build_prompt(process_name, business_purpose_raw, category, evidence_chunks)
        r = httpx.post(
            f"{self._base_url}/api/generate",
            json={"model": self._model, "prompt": prompt, "stream": False, "options": {"temperature": 0.2}},
            timeout=settings.llm_timeout_seconds,
        )
        r.raise_for_status()
        raw_text = r.json().get("response", "")
        data = _extract_json(raw_text)
        data["model_used"] = f"ollama:{self._model}"
        return data
