import json
from typing import Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from ai.llm_client import LLMClient, build_prompt


class OpenAIClient(LLMClient):
    def __init__(self):
        self._client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def is_available(self) -> bool:
        return self._client is not None

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
    def analyze_process(self, process_name: str, business_purpose_raw: str,
                         category: Optional[str], evidence_chunks: list[str]) -> dict:
        prompt = build_prompt(process_name, business_purpose_raw, category, evidence_chunks)
        resp = self._client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a precise enterprise process analyst. Output strict JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            timeout=settings.llm_timeout_seconds,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        data = json.loads(content)
        data["model_used"] = settings.openai_model
        return data
