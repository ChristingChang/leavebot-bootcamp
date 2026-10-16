"""LLM 介面。業務程式只依賴 LLMClient，測試時換成 FakeLLM，不花錢、結果固定。

三種真的模型：
- ClaudeCliLLM：借用本機已登入的 Claude Code（訂閱制即可，不用 API key）
- AnthropicLLM：呼叫 Claude API（要 API key）
- 其他供應商：寫一個有 complete(system=..., user=...) 方法的類別，加進 build_llm
"""

import json
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from typing import Any, Protocol

import anthropic

from app.config import Settings

FALLBACK_BETA = "server-side-fallback-2026-07-01"
DEFAULT_MAX_TOKENS = 16000
CLI_TIMEOUT_SECONDS = 120


class LLMError(RuntimeError):
    """呼叫模型失敗，或回傳的東西不能用。"""


class LLMClient(Protocol):
    def complete(self, *, system: str, user: str) -> str: ...


class FakeLLM:
    """依序回傳預先寫好的字串。用完之後回傳 default；沒有 default 就報錯。"""

    def __init__(self, responses: Sequence[str] = (), default: str | None = None) -> None:
        self._responses = tuple(responses)
        self._default = default
        self.calls: tuple[tuple[str, str], ...] = ()

    def complete(self, *, system: str, user: str) -> str:
        index = len(self.calls)
        self.calls = self.calls + ((system, user),)
        if index < len(self._responses):
            return self._responses[index]
        if self._default is not None:
            return self._default
        raise LLMError(f"FakeLLM 只準備了 {len(self._responses)} 個回應，這是第 {index + 1} 次呼叫")


class AnthropicLLM:
    """呼叫 Claude。模型拒答時，伺服器端會自動改由備援模型回答（fallbacks="default"）。"""

    def __init__(self, model: str, client: Any = None, max_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        self._model = model
        self._client = client if client is not None else anthropic.Anthropic()
        self._max_tokens = max_tokens

    def complete(self, *, system: str, user: str) -> str:
        try:
            response = self._client.beta.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
                betas=[FALLBACK_BETA],
                fallbacks="default",
            )
        except anthropic.APIConnectionError as exc:
            raise LLMError(f"連不上 Claude API：{exc}") from exc
        except anthropic.RateLimitError as exc:
            raise LLMError("Claude API 請求太頻繁，稍後再試") from exc
        except anthropic.APIStatusError as exc:
            raise LLMError(f"Claude API 回傳錯誤 {exc.status_code}：{exc.message}") from exc

        if response.stop_reason == "refusal":
            raise LLMError("模型拒絕回答這個請求")
        if response.stop_reason == "max_tokens":
            raise LLMError("回應被 max_tokens 截斷，內容不完整")

        text = "".join(block.text for block in response.content if block.type == "text")
        if not text.strip():
            raise LLMError("模型回應裡沒有文字內容")
        return text


class ClaudeCliLLM:
    """透過 `claude -p` 呼叫模型，用的是本機 Claude Code 的登入（訂閱或 API key 皆可）。

    三個刻意的設定：
    - 工具全關（--tools ""）：它只負責把文字變成文字，讀不到檔案、跑不了指令。
      被注入的請假句子最多讓輸出變怪，不能讓它去碰你的電腦。
    - 在空的暫存目錄執行：不會讀到這個專案的 AGENTS.md / CLAUDE.md 與技能。
    - 使用者的句子走 stdin，不放在指令參數裡：以 - 開頭的句子不會被當成旗標。
    """

    def __init__(
        self,
        model: str = "",
        run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
        timeout: int = CLI_TIMEOUT_SECONDS,
    ) -> None:
        self._model = model
        self._run = run
        self._timeout = timeout

    def _command(self, system: str) -> list[str]:
        command = [
            "claude", "-p",
            "--output-format", "json",
            "--tools", "",
            "--no-session-persistence",
            "--setting-sources", "",
            "--strict-mcp-config",
            "--system-prompt", system,
        ]
        if self._model:
            command += ["--model", self._model]
        return command

    def complete(self, *, system: str, user: str) -> str:
        with tempfile.TemporaryDirectory(prefix="leavebot-llm-") as workdir:
            try:
                completed = self._run(
                    self._command(system),
                    input=user,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout,
                    cwd=workdir,
                )
            except FileNotFoundError as exc:
                raise LLMError("找不到 claude 指令：先安裝 Claude Code 並登入（打 claude 能進去就對了）") from exc
            except subprocess.TimeoutExpired as exc:
                raise LLMError(f"claude 超過 {self._timeout} 秒沒有回應（逾時）") from exc

        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()
            raise LLMError(f"claude 執行失敗（exit {completed.returncode}）：{detail}")

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise LLMError(f"看不懂 claude 的輸出：{completed.stdout[:200]}") from exc

        text = str(payload.get("result", ""))
        if payload.get("is_error"):
            raise LLMError(f"claude 回報錯誤：{text}")
        if not text.strip():
            raise LLMError("模型回應裡沒有文字內容")
        return text


def build_llm(settings: Settings) -> LLMClient:
    if settings.llm_provider == "anthropic":
        return AnthropicLLM(model=settings.llm_model)
    if settings.llm_provider == "claude-cli":
        return ClaudeCliLLM(model=settings.llm_model)
    return FakeLLM(default="{}")
