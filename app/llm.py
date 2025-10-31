from __future__ import annotations

import os
from typing import Any, Dict

import httpx


class GroqChat:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set")
        self._api_key = api_key
        self._model = model_name
        self._base_url = "https://api.groq.com/openai/v1/chat/completions"

    async def complete(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 512,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self._base_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"] or ""


