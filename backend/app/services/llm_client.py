from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


class LLMClient:
    """Small wrapper around OpenAI Responses API with retry and mock support."""

    def __init__(
        self,
        *,
        timeout_s: float = 20.0,
        retries: int = 2,
        model: str = "gpt-4o-mini",
        mock: bool | None = None,
        api_key: str | None = None,
        prompts_dir: Path | None = None,
    ) -> None:
        env_mock = _is_truthy(os.getenv("LLM_MOCK"))
        self.mock = env_mock if mock is None else mock
        self.timeout_s = timeout_s
        self.retries = max(retries, 0)
        self.model = model
        self.api_key = api_key or settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
        self.prompts_dir = prompts_dir or Path(__file__).resolve().parents[1] / "prompts"
        self._client: Any | None = None

        if not self.mock and not self.api_key:
            raise ValueError("OpenAI API key is required when LLM_MOCK is not enabled")

    def run_prompt(self, prompt_name: str, input_json: dict[str, Any]) -> Any:
        prompt_text = self._load_prompt(prompt_name)
        self._log_event(
            "llm.request.started",
            prompt_name=prompt_name,
            mock=self.mock,
            retries=self.retries,
            timeout_s=self.timeout_s,
        )

        if self.mock:
            output = self._mock_response(prompt_name=prompt_name, input_json=input_json)
            self._log_event("llm.request.mock_response", prompt_name=prompt_name, output=output)
            return output

        messages = [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": json.dumps(input_json, ensure_ascii=False, sort_keys=True)},
        ]

        for attempt in range(self.retries + 1):
            try:
                response = self._openai_client().responses.create(
                    model=self.model,
                    input=messages,
                    timeout=self.timeout_s,
                )
                text_output = response.output_text.strip()
                parsed_output = self._to_json_if_possible(text_output)
                self._log_event(
                    "llm.request.succeeded",
                    prompt_name=prompt_name,
                    attempt=attempt,
                    output_type=type(parsed_output).__name__,
                )
                return parsed_output
            except Exception as exc:  # noqa: BLE001 - keep retry logic generic
                self._log_event(
                    "llm.request.failed",
                    prompt_name=prompt_name,
                    attempt=attempt,
                    error=str(exc),
                )
                if attempt >= self.retries:
                    raise
                time.sleep(0.5 * (attempt + 1))

        raise RuntimeError("Unexpected retry flow in LLMClient")

    def _openai_client(self) -> Any:
        if self._client is not None:
            return self._client

        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise RuntimeError(
                "Package 'openai' is required when LLM_MOCK is disabled"
            ) from exc

        self._client = OpenAI(api_key=self.api_key)
        return self._client

    def _load_prompt(self, prompt_name: str) -> str:
        filename = prompt_name if prompt_name.endswith(".md") else f"{prompt_name}.md"
        prompt_path = self.prompts_dir / filename

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        return prompt_path.read_text(encoding="utf-8")

    def _mock_response(self, *, prompt_name: str, input_json: dict[str, Any]) -> dict[str, Any]:
        canonical_input = json.dumps(input_json, ensure_ascii=False, sort_keys=True)
        mock_id = hashlib.sha256(f"{prompt_name}:{canonical_input}".encode("utf-8")).hexdigest()[:12]
        return {
            "mode": "mock",
            "prompt_name": prompt_name,
            "mock_id": mock_id,
            "received": input_json,
            "result": f"Mock response for {prompt_name} ({mock_id})",
        }

    @staticmethod
    def _to_json_if_possible(text: str) -> Any:
        if not text:
            return ""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text

    @staticmethod
    def _log_event(event: str, **fields: Any) -> None:
        payload = {"event": event, **fields}
        logger.info(json.dumps(payload, ensure_ascii=False, default=str))


_default_client: LLMClient | None = None


def run_prompt(prompt_name: str, input_json: dict[str, Any]) -> Any:
    """Run a versioned prompt and return parsed JSON output when possible."""

    global _default_client
    if _default_client is None:
        _default_client = LLMClient(
            timeout_s=settings.llm_timeout_s,
            retries=settings.llm_retries,
            model=settings.llm_model,
            mock=settings.llm_mock,
        )
    return _default_client.run_prompt(prompt_name=prompt_name, input_json=input_json)
