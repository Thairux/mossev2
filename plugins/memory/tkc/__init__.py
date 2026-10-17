"""TKC memory provider — native TKC (Token Cache Compressor) memory for mosse.

Mosse never opens ``tkc.db`` directly. It shells out to the ``tkc`` CLI (bundled
by default, overridable via config) which is the single source of truth for
content-addressed, hash-verified memory shared across Hermes, OpenCode, and mosse.

Config fields (config_schema.py):
  tkc_path   — path to the TKC CLI executable (default: "tkc" on PATH)
  tkc_home   — TKC home directory (default: ~/.tkc)

Graceful degradation: if TKC is unavailable at boot, mosse starts normally with
a warning and memory features are disabled until TKC becomes available.

TKC CLI commands wrapped (see tkc/src/cli.ts for the reference surface):
  compress, expand, recall, fingerprint, board [feed|digest], handoff latest,
  comment add, comments, outline, grep, history, snapshot, restore, write,
  rule-add, rule-for, rules, docs
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import threading
from datetime import datetime, timezone, UTC
from pathlib import Path
from typing import Any, Callable, Optional

from agent.memory_provider import MemoryProvider, PRE_COMPRESS_CHECKPOINT_API_VERSION, RecallStatus, spawn_context_thread, ctx_bound
from agent.secret_scope import get_secret
from tools.registry import tool_error

logger = logging.getLogger(__name__)

_DEFAULT_TKC_PATH = "tkc"
_TKC_HOME_ENV = "TKC_HOME"

_SCHEMAS = [
    {
        "name": "tkc_recall",
        "description": "Search TKC memory (content-addressed, hash-verified) for context relevant to a query. Same-project exact slug first, then cross-project FTS. Returns up to 25 refs.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for in TKC memory."},
                "top_k": {"type": "integer", "description": "Max results (default: 8, max: 25).", "default": 8, "minimum": 1, "maximum": 25},
            },
            "required": ["query"],
        },
    },
    {
        "name": "tkc_expand",
        "description": "Restore full, hash-verified text for a TKC slug. Byte-exact — never a summary.",
        "parameters": {
            "type": "object",
            "properties": {
                "slug": {"type": "string", "description": "TKC slug (short ref from tkc_recall or a tkc: reference)."},
            },
            "required": ["slug"],
        },
    },
    {
        "name": "tkc_remember",
        "description": "Persist a fact, preference, or decision to TKC memory as a content-addressed block with a short ref.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "The fact, preference, or decision to remember."},
                "kind": {"type": "string", "description": "Kind: note | decision | rule | question | status | handoff (default: note).", "default": "note", "enum": ["note", "decision", "rule", "question", "status", "handoff"]},
                "slug": {"type": "string", "description": "Optional slug/key to store under (auto-generated if omitted)."},
            },
            "required": ["content"],
        },
    },
    {
        "name": "tkc_profile",
        "description": "Get the user's TKC fingerprint (CORE tier: who they are and how they work). Call at session start to inject user context.",
        "parameters": {
            "type": "object",
            "properties": {
                "tier": {"type": "string", "description": "Fingerprint tier: core | detail | decisions (default: core).", "default": "core"},
            },
        },
    },
    {
        "name": "tkc_board",
        "description": "Read the TKC message board — session handoffs, status, blockers, and questions left by agents.",
        "parameters": {
            "type": "object",
            "properties": {
                "mode": {"type": "string", "description": "feed | digest (default: digest).", "default": "digest"},
            },
        },
    },
    {
        "name": "tkc_comment",
        "description": "Attach a note, rule, decision, question, status, or handoff comment to a TKC target (slug, symbol, hash, or path).",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "TKC target to attach the comment to."},
                "body": {"type": "string", "description": "Comment body text."},
                "kind": {"type": "string", "description": "Kind: note | decision | rule | question | status | handoff (default: note).", "default": "note"},
            },
            "required": ["target", "body"],
        },
    },
    {
        "name": "tkc_rules_for",
        "description": "Get TKC rules that apply to a file path (scoped rule engine).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to check rules for."},
            },
            "required": ["path"],
        },
    },
]

_tool_handlers: dict[str, Callable[..., Any]] = {}


def _load_tkc_config() -> dict[str, Any]:
    """``memory.tkc`` block from config.yaml (empty on error)."""
    try:
        from hermes_cli.config import load_config_readonly
        block = load_config_readonly().get("memory", {}).get("tkc", {})
    except Exception:
        block = None
    return dict(block) if isinstance(block, dict) else {}


def _resolve_tkc_path() -> str:
    """Resolve the TKC CLI path: config > env > default 'tkc' on PATH."""
    cfg = _load_tkc_config()
    path = cfg.get("tkc_path") or os.environ.get("TKC_PATH") or _DEFAULT_TKC_PATH
    return str(path).strip()


def _resolve_tkc_home() -> Optional[str]:
    """Resolve TKC home directory: config > env TKC_HOME > None (TKC defaults to ~/.tkc)."""
    cfg = _load_tkc_config()
    home = cfg.get("tkc_home") or os.environ.get(_TKC_HOME_ENV)
    return str(home).strip() if home else None


def _tkc_env() -> dict[str, str]:
    """Build the environment for TKC subprocess calls (inherit + TKC_HOME if set)."""
    env = dict(os.environ)
    home = _resolve_tkc_home()
    if home:
        env["TKC_HOME"] = home
    return env


def _run_tkc(args: list[str], *, input_text: Optional[str] = None, timeout: float = 30.0) -> tuple[int, str, str]:
    """Run the TKC CLI with *args*; return (exit_code, stdout, stderr)."""
    tkc_path = _resolve_tkc_path()
    try:
        proc = subprocess.run(
            [tkc_path] + args,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_tkc_env(),
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", f"TKC CLI not found at '{tkc_path}' (install TKC or set memory.tkc.tkc_path)"
    except subprocess.TimeoutExpired:
        return 124, "", f"TKC CLI timed out after {timeout}s"
    except OSError as exc:  # pragma: no cover - platform-specific exec errors
        return 1, "", f"TKC CLI failed to start: {exc}"


def _parse_json(stdout: str, stderr: str, exit_code: int, label: str) -> Optional[Any]:
    """Parse TKC CLI JSON output; log and return None on failure."""
    if exit_code != 0:
        logger.debug("TKC %s exited %d: %s", label, exit_code, stderr.strip()[:200])
        return None
    text = (stdout or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        logger.warning("TKC %s returned non-JSON output: %s", label, exc)
        return None


class TKCMemoryProvider(MemoryProvider):
    """TKC (Token Cache Compressor) memory provider.

    Shells out to the TKC CLI. TKC is the shared brain: content-addressed blocks,
    hash-verified restore, append-only history, comments, symbol index, fingerprint,
    board, and handoffs — shared across Hermes, OpenCode, and mosse.
    """

    pre_compress_checkpoint_api_version = PRE_COMPRESS_CHECKPOINT_API_VERSION

    def __init__(self):
        self._tkc_path: Optional[str] = None
        self._tkc_home: Optional[str] = None
        self._hermes_home: Optional[Path] = None
        self._session_id: str = ""
        self._user_id: str = "default"
        self._initialized: bool = False
        self._available: bool = False
        self._lock = threading.Lock()
        self._last_recall_count: int = 0
        self._last_recall_label: str = "tkc"

    @property
    def name(self) -> str:
        return "tkc"

    def is_available(self) -> bool:
        """TKC is available when the CLI resolves and responds to a fingerprint call."""
        if not self._initialized:
            # Pre-init availability: check if the CLI exists on PATH/config path.
            code, _, _ = _run_tkc(["fingerprint", "core"], timeout=10.0)
            return code == 0
        return self._available

    def unavailable_reason(self) -> str:
        if not self._initialized:
            return "TKC CLI not found — install TKC (https://github.com/Thairux/tkc) or set memory.tkc.tkc_path in config.yaml."
        if not self._available:
            return "TKC CLI did not respond — memory features are disabled until TKC is reachable."
        return ""

    def initialize(self, session_id: str, **kwargs) -> None:
        """Initialize TKC provider: resolve CLI path, verify availability, bind session."""
        self._hermes_home = Path(kwargs.get("hermes_home", "") or "")
        self._session_id = session_id
        self._user_id = str(kwargs.get("user_id", "default") or "default")
        self._tkc_path = _resolve_tkc_path()
        self._tkc_home = _resolve_tkc_home()
        self._initialized = True

        # Verify TKC CLI is reachable (graceful degradation: failure is non-fatal).
        code, _, stderr = _run_tkc(["fingerprint", "core"], timeout=10.0)
        self._available = code == 0
        if not self._available:
            logger.warning("TKC provider initialized but TKC CLI unavailable: %s", stderr.strip()[:200] or "(no output)")
        else:
            logger.info("TKC memory provider initialized (CLI: %s, home: %s)", self._tkc_path, self._tkc_home or "<default>")

    def system_prompt_block(self) -> str:
        """STATIC system-prompt block advertising TKC memory availability."""
        if not self._available:
            return "# TKC Memory\nUnavailable (TKC CLI not reachable). Install TKC or set memory.tkc.tkc_path to enable."
        return (
            "# TKC Memory\n"
            "Active. TKC is mosse's content-addressed, hash-verified shared brain. "
            "Use tkc_recall to find relevant context, tkc_expand to restore full text, "
            "tkc_remember to store facts/preferences/decisions, tkc_profile for the user fingerprint, "
            "tkc_board for session handoffs, tkc_comment to attach notes/rules/decisions, "
            "and tkc_rules_for to get scoped rules for a file path."
        )

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        """Return formatted TKC recall context for the upcoming turn."""
        if not self._available:
            return ""
        query = (query or "").strip()
        if not query:
            return ""
        code, stdout, stderr = _run_tkc(["recall", query], timeout=15.0)
        data = _parse_json(stdout, stderr, code, "recall")
        if data is None:
            return ""
        refs = data.get("refs", []) if isinstance(data, dict) else []
        count = len(refs)
        with self._lock:
            self._last_recall_count = count
            self._last_recall_label = "tkc"
        if not refs:
            return ""
        lines = ["[TKC Memory]", "Relevant context:"]
        for ref in refs[:8]:
            slug = ref.get("slug") or ref.get("id") or ""
            preview = (ref.get("preview") or ref.get("text") or "")[:200]
            if slug:
                lines.append(f"- {slug}: {preview}")
            else:
                lines.append(f"- {preview}")
        return "\n".join(lines)

    def queue_prefetch(self, query: str, *, session_id: str = "") -> None:
        """Queue a background TKC recall after each turn (no-op: recall is on-demand via prefetch)."""
        # TKC recall is lightweight and synchronous; no background queue needed.
        # Kept for interface compliance.
        pass

    def recall_status(self) -> Optional[RecallStatus]:
        """What the most recent prefetch injected."""
        with self._lock:
            count = self._last_recall_count
            label = self._last_recall_label
        if count <= 0:
            return None
        return RecallStatus(provider_label=label, count=count)

    def sync_turn(
        self,
        user_content: str,
        assistant_content: str,
        *,
        session_id: str = "",
        messages: Optional[list[dict[str, Any]]] = None,
        turn_author: Optional[dict[str, Any]] = None,
    ) -> None:
        """Persist a completed turn to TKC: compress the turn into a block with a dated slug."""
        if not self._available or not user_content:
            return
        # Build a dated slug for this turn.
        now = datetime.now(UTC)
        slug = f"turn/{now.strftime('%Y-%m-%d')}/{self._user_id}/{now.strftime('%H%M%S')}"
        # Compress turn content into TKC as a single block.
        text = f"[{now.isoformat()}] user: {user_content}\nassistant: {assistant_content or ''}"
        _run_tkc(["compress", slug], input_text=text, timeout=15.0)
        # Also store as a write-through entry for durability.
        _run_tkc(["write", slug, text], timeout=15.0)

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        """Return TKC tool schemas; empty if TKC is unavailable."""
        if not self._available:
            return []
        return list(_SCHEMAS)

    def handle_tool_call(self, tool_name: str, args: dict[str, Any], **kwargs) -> str:
        """Handle one TKC tool call; returns a JSON string."""
        if not self._available:
            return tool_error("TKC memory provider is unavailable (TKC CLI not reachable).")
        handler = _tool_handlers.get(tool_name)
        if handler is None:
            return tool_error(f"Unknown TKC tool: {tool_name}")
        try:
            result = handler(self, args)
            return json.dumps(result, ensure_ascii=False)
        except Exception as exc:
            logger.error("TKC tool '%s' failed: %s", tool_name, exc)
            return tool_error(f"TKC tool '{tool_name}' failed: {exc}")

    def on_memory_write(self, action: str, target: str, content: str, metadata: Optional[dict[str, Any]] = None) -> None:
        """Mirror built-in memory-tool writes to TKC."""
        if not self._available or action != "add" or not content:
            return
        slug = metadata.get("slug") if metadata else None
        if not slug:
            # Derive a slug from the target and a hash of content.
            import hashlib
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
            slug = f"memory/{target or 'user'}/{digest}"
        _run_tkc(["write", slug, content], timeout=15.0)
        # Attach a comment with the kind.
        kind = (metadata.get("kind") if metadata else None) or "note"
        _run_tkc(["comment", "add", slug, kind, content], timeout=10.0)

    def on_session_end(self, messages: list[dict[str, Any]]) -> None:
        """End-of-session extraction: compress the session into a TKC block + board post."""
        if not self._available or not messages:
            return
        # Compress the last N messages into a session summary block.
        recent = messages[-10:] if len(messages) > 10 else messages
        parts = []
        for m in recent:
            role = m.get("role", "?")
            content = m.get("content", "")
            parts.append(f"{role}: {content}")
        session_text = "\n".join(parts)
        now = datetime.now(UTC)
        slug = f"session/{now.strftime('%Y-%m-%d')}/{self._user_id}/{now.strftime('%H%M%S')}"
        _run_tkc(["write", slug, session_text], timeout=15.0)
        # Post a handoff to the TKC board.
        summary = session_text[:500] + ("..." if len(session_text) > 500 else "")
        _run_tkc(["board", summary], timeout=10.0)

    def shutdown(self) -> None:
        """Clean shutdown — no persistent connections to close (CLI is stateless)."""
        self._initialized = False
        self._available = False

    def get_config_schema(self) -> list[dict[str, Any]]:
        """Setup fields for ``hermes memory setup``."""
        return [
            {
                "key": "tkc_path",
                "description": "Path to the TKC CLI executable.",
                "secret": False,
                "required": False,
                "default": _DEFAULT_TKC_PATH,
                "env_var": "TKC_PATH",
            },
            {
                "key": "tkc_home",
                "description": "TKC home directory (default: ~/.tkc).",
                "secret": False,
                "required": False,
                "default": "",
                "env_var": "TKC_HOME",
            },
        ]

    def save_config(self, values: dict[str, Any], hermes_home: str) -> None:
        """Write non-secret setup values to the TKC provider's native config."""
        # TKC config lives in config.yaml memory.tkc block; nothing to write natively.
        # The hermes_cli config system persists the block automatically.
        pass


# --- TKC tool handlers -------------------------------------------------------

def _tkc_recall(provider: TKCMemoryProvider, args: dict) -> dict:
    query = args.get("query", "").strip()
    top_k = min(int(args.get("top_k", 8)), 25)
    code, stdout, stderr = _run_tkc(["recall", query], timeout=15.0)
    data = _parse_json(stdout, stderr, code, "recall")
    if data is None:
        return {"error": f"TKC recall failed: {stderr.strip() or '(no output)'}"}
    refs = data.get("refs", []) if isinstance(data, dict) else []
    with provider._lock:
        provider._last_recall_count = len(refs)
        provider._last_recall_label = "tkc"
    return {"refs": refs[:top_k], "count": len(refs), "query": query}


def _tkc_expand(provider: TKCMemoryProvider, args: dict) -> dict:
    slug = args.get("slug", "").strip()
    if not slug:
        return {"error": "slug is required"}
    code, stdout, stderr = _run_tkc(["expand", slug], timeout=15.0)
    if code != 0:
        return {"error": f"TKC expand failed: {stderr.strip() or '(no output)'}"}
    return {"slug": slug, "content": stdout}


def _tkc_remember(provider: TKCMemoryProvider, args: dict) -> dict:
    content = args.get("content", "").strip()
    kind = args.get("kind", "note")
    slug = args.get("slug", "").strip() or f"memory/{kind}/{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    # Store as a write-through block.
    code, stdout, stderr = _run_tkc(["write", slug, content], timeout=15.0)
    if code != 0:
        return {"error": f"TKC remember failed: {stderr.strip() or '(no output)'}"}
    # Attach a comment with the kind.
    _run_tkc(["comment", "add", slug, kind, content], timeout=10.0)
    return {"slug": slug, "kind": kind, "stored": True}


def _tkc_profile(provider: TKCMemoryProvider, args: dict) -> dict:
    tier = args.get("tier", "core")
    code, stdout, stderr = _run_tkc(["fingerprint", tier], timeout=10.0)
    if code != 0:
        return {"error": f"TKC fingerprint failed: {stderr.strip() or '(no output)'}"}
    try:
        return {"tier": tier, "profile": json.loads(stdout)}
    except json.JSONDecodeError:
        return {"tier": tier, "profile": stdout}


def _tkc_board(provider: TKCMemoryProvider, args: dict) -> dict:
    mode = args.get("mode", "digest")
    code, stdout, stderr = _run_tkc(["board", mode], timeout=10.0)
    if code != 0:
        return {"error": f"TKC board failed: {stderr.strip() or '(no output)'}"}
    try:
        return {"mode": mode, "board": json.loads(stdout)}
    except json.JSONDecodeError:
        return {"mode": mode, "board": stdout}


def _tkc_comment(provider: TKCMemoryProvider, args: dict) -> dict:
    target = args.get("target", "").strip()
    body = args.get("body", "").strip()
    kind = args.get("kind", "note")
    if not target or not body:
        return {"error": "target and body are required"}
    code, stdout, stderr = _run_tkc(["comment", "add", target, kind, body], timeout=10.0)
    if code != 0:
        return {"error": f"TKC comment failed: {stderr.strip() or '(no output)'}"}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"target": target, "kind": kind, "posted": True}


def _tkc_rules_for(provider: TKCMemoryProvider, args: dict) -> dict:
    path = args.get("path", "").strip()
    if not path:
        return {"error": "path is required"}
    code, stdout, stderr = _run_tkc(["rule-for", path], timeout=10.0)
    if code != 0:
        return {"error": f"TKC rules-for failed: {stderr.strip() or '(no output)'}"}
    try:
        return {"path": path, "rules": json.loads(stdout)}
    except json.JSONDecodeError:
        return {"path": path, "rules": stdout}


_tool_handlers = {
    "tkc_recall": _tkc_recall,
    "tkc_expand": _tkc_expand,
    "tkc_remember": _tkc_remember,
    "tkc_profile": _tkc_profile,
    "tkc_board": _tkc_board,
    "tkc_comment": _tkc_comment,
    "tkc_rules_for": _tkc_rules_for,
}


def register(ctx) -> None:
    """Register TKC as a memory provider plugin."""
    ctx.register_memory_provider(TKCMemoryProvider())
