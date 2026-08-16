#!/usr/bin/env python3
"""Minimal local skills store CLI.

Features:
- Reads a local index JSON from file:// URI (or plain path).
- Search skills by keyword.
- Install a skill zip into a target directory.
- List locally installed skills from a lock file.
- Upgrade installed skills from update manifest defined in skill config.json.
- Self-upgrade the CLI binary/script from an update manifest URL in config.json.
"""

import argparse
import base64
import functools
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from skills_upgrade import cmd_upgrade as run_skills_upgrade


DEFAULT_INSTALL_ROOT = "./skills"
LOCKFILE_NAME = ".skills_store_lock.json"
SKILL_CONFIG_NAME = "config.json"
SKILL_META_NAME = "_meta.json"
CLI_CONFIG_NAME = "config.json"
# sandbox run 会话复用缓存：按 host+skills 组合分桶记录 session_id / last_used，
# 默认 30 分钟滑动窗口内同组 skills 复用同一会话。
RUN_SESSIONS_FILE_NAME = "run_sessions.json"
DEFAULT_RUN_SESSION_TTL = 1800
CLI_VERSION_FILE_NAME = "version.json"
CLI_METADATA_FILE_NAME = "metadata.json"
CLI_VERSION_FALLBACK = "2026.3.3"
DEFAULT_INDEX_URI_FALLBACK = "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/skills.json"
DEFAULT_SEARCH_URL_FALLBACK = "https://api.skillhub.cn/api/v1/search"
SELF_UPGRADE_CHECK_TIMEOUT_SECONDS = 2
DEFAULT_CLI_HOME = "~/.skillhub"
SELF_UPGRADE_REEXEC_ENV = "SKILLHUB_SELF_UPGRADE_REEXEC"
SKIP_SELF_UPGRADE_ENV = "SKILLHUB_SKIP_SELF_UPGRADE"
SKIP_WORKSPACE_SKILLS_ENV = "SKILLHUB_SKIP_WORKSPACE_SKILLS"
# Override the interactive-prompt decision (mainly for tests / CI rehearsal).
# Set to "yes"/"no" to auto-answer; set to "skip" to behave like non-interactive.
SELF_UPGRADE_PROMPT_ANSWER_ENV = "SKILLHUB_SELF_UPGRADE_ANSWER"
IGNORED_SELF_UPDATE_VERSION_KEY = "ignored_self_update_version"
DEFAULT_SELF_UPDATE_MANIFEST_URL_FALLBACK = "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/version.json"
DEFAULT_SKILLS_DOWNLOAD_URL_TEMPLATE_FALLBACK = (
    "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/skills/{slug}.zip"
)
DEFAULT_PRIMARY_DOWNLOAD_URL_TEMPLATE_FALLBACK = (
    "https://api.skillhub.cn/api/v1/download?slug={slug}"
)
DEFAULT_OPENCLAW_CONFIG_PATH = "~/.openclaw/openclaw.json"
DEFAULT_OPENCLAW_WORKSPACE_PATH = "~/.openclaw/workspace"
DEFAULT_OPENCLAW_PLUGIN_DIR = "~/.openclaw/extensions/skillhub"
POST_UPGRADE_SKILL_MIGRATION_MIN_VERSION = (3, 13)
FIND_SKILLS_SLUG = "find-skills"
SKILLHUB_PREFERENCE_SLUG = "skillhub-preference"
RANKING_ENDPOINTS = {
    "hot": "/api/v1/showcase/hot",
    "featured": "/api/v1/showcase/featured",
    "newest": "/api/v1/showcase/newest",
    "recommended": "/api/v1/showcase/recommended",
    "trending": "/api/v1/showcase/trending",
    "paid": "/api/v1/showcase/paid",
}
SECURITY_REPORT_SOURCES = (
    ("keen", "keen", "keen-xti", "科恩实验室"),
    ("keen-xti", "keen", "keen-xti", "科恩实验室"),
    ("sanbu", "yunding", "tencent-sanbu", "云鼎实验室"),
    ("tencent-sanbu", "yunding", "tencent-sanbu", "云鼎实验室"),
)


def load_cli_version(base_dir: Path) -> str:
    version_path = base_dir / CLI_VERSION_FILE_NAME
    if not version_path.exists():
        return CLI_VERSION_FALLBACK
    try:
        raw = json.loads(version_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return CLI_VERSION_FALLBACK
    if not isinstance(raw, dict):
        return CLI_VERSION_FALLBACK
    value = raw.get("version")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return CLI_VERSION_FALLBACK


def load_cli_metadata(base_dir: Path) -> Dict[str, str]:
    metadata_path = base_dir / CLI_METADATA_FILE_NAME
    if not metadata_path.exists():
        return {}
    try:
        raw = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(raw, dict):
        return {}
    out: Dict[str, str] = {}
    for key in (
        "skills_index_url",
        "skills_download_url_template",
        "self_update_manifest_url",
        "skills_search_url",
        "skills_primary_download_url_template",
    ):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            out[key] = value.strip()
    return out


def default_search_url(metadata: Dict[str, str]) -> str:
    explicit = os.environ.get("SKILLHUB_SEARCH_URL", "").strip()
    if explicit:
        return explicit
    host = os.environ.get("SKILLHUB_HOST", "").strip()
    if host:
        parsed = urllib.parse.urlparse(host)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            return urllib.parse.urljoin(host.rstrip("/") + "/", "api/v1/search")
    return metadata.get("skills_search_url", DEFAULT_SEARCH_URL_FALLBACK)


CLI_VERSION = load_cli_version(Path(__file__).resolve().parent)
CLI_METADATA = load_cli_metadata(Path(__file__).resolve().parent)
DEFAULT_INDEX_URI = CLI_METADATA.get("skills_index_url", DEFAULT_INDEX_URI_FALLBACK)
DEFAULT_SELF_UPDATE_MANIFEST_URL = CLI_METADATA.get(
    "self_update_manifest_url",
    DEFAULT_SELF_UPDATE_MANIFEST_URL_FALLBACK,
)
DEFAULT_SKILLS_DOWNLOAD_URL_TEMPLATE = CLI_METADATA.get(
    "skills_download_url_template",
    DEFAULT_SKILLS_DOWNLOAD_URL_TEMPLATE_FALLBACK,
)
DEFAULT_SEARCH_URL = default_search_url(CLI_METADATA)
DEFAULT_PRIMARY_DOWNLOAD_URL_TEMPLATE = (
    os.environ.get("SKILLHUB_PRIMARY_DOWNLOAD_URL_TEMPLATE", "").strip()
    or CLI_METADATA.get(
        "skills_primary_download_url_template",
        DEFAULT_PRIMARY_DOWNLOAD_URL_TEMPLATE_FALLBACK,
    )
)
CLI_USER_AGENT = f"skills-store-cli/{CLI_VERSION}"
CLI_CLIENT_ID_CONFIG_KEY = "client_id"
CLI_CLIENT_ID_HEADER = "X-SkillHub-Client-Id"
_CLI_CLIENT_ID_CACHE: Optional[str] = None

# ============================================================
# CLI 调用方 agent 类型识别（caller_type）
# ------------------------------------------------------------
# 4 层优先级投票：
#   L0 显式 env `SKILLHUB_CALLER` / config `caller_override`（最高优先级）
#   L1 目录印记（cwd 及祖先，区分 project 层 vs $HOME 层）——主信号
#   L2 环境变量印记（各 agent 注入的 env）——L1 落空 / 或与 home 层交集时决胜
#   L3 父进程名（psutil / ps 兜底，缺失则跳过）
# 全部未命中 → 若 tty 交互则 raw-shell，否则 unknown。
# ⭐ 白名单必须与后端 middleware_cli_usage.go 的 cliCallerWhitelist 严格对齐。
# ============================================================

# 目录印记 → caller_type 枚举
DIR_MARKERS: Dict[str, str] = {
    ".codebuddy":       "codebuddy",
    ".openclaw":        "openclaw",
    ".hemers":          "hemers",
    ".codex":           "codex",
    ".claude":          "claude-code",
    "CLAUDE.md":        "claude-code",
    ".cursor":          "cursor",
    ".cursorrules":     "cursor",
    ".gemini":          "gemini-cli",
    ".qwen":            "qwen-code",
    ".windsurf":        "windsurf",
    ".windsurfrules":   "windsurf",
    ".cline":           "cline",
    ".clinerules":      "cline",
    ".roo":             "roo-code",
    ".roomodes":        "roo-code",
    ".continue":        "continue",
    ".aider.conf.yml":  "aider",
    ".opencode":        "opencode",
    ".openhands":       "openhands",
    ".trae":            "trae",
    ".kiro":            "kiro",
    ".devin":           "devin",
}

# 环境变量印记 → caller_type 枚举（只做键存在性判断）
ENV_MARKERS: Dict[str, str] = {
    "CODEBUDDY_SESSION_ID":   "codebuddy",
    "OPENCLAW_HOME":          "openclaw",
    "OPENCLAW_SESSION_ID":    "openclaw",
    "HEMERS_HOME":            "hemers",
    "HEMERS_SESSION_ID":      "hemers",
    "CLAUDECODE":             "claude-code",
    "CLAUDE_CODE_ENTRYPOINT": "claude-code",
    "CODEX_HOME":             "codex",
    "CODEX_SESSION_ID":       "codex",
    "CURSOR_TRACE_ID":        "cursor",
    "CURSOR_SESSION":         "cursor",
    "GITHUB_COPILOT_AGENT":   "github-copilot",
    "COPILOT_AGENT":          "github-copilot",
    "GEMINI_CLI":             "gemini-cli",
    "QWEN_CODE":              "qwen-code",
    "QWEN_CODE_SESSION":      "qwen-code",
    "AMAZON_Q":               "amazon-q",
    "AMAZON_Q_CLI":           "amazon-q",
    "WINDSURF_SESSION":       "windsurf",
    "CLINE_SESSION":          "cline",
    "ROO_CODE":               "roo-code",
    "CONTINUE_SESSION_ID":    "continue",
    "AIDER":                  "aider",
    "OPENCODE":               "opencode",
    "OPENHANDS":              "openhands",
    "TRAE_SESSION":           "trae",
    "KIRO_SESSION":           "kiro",
    "DEVIN_SESSION_ID":       "devin",
    "REPLIT_AGENT":           "replit-agent",
}

# 父进程名印记（basename） → caller_type 枚举
# node/python/sh/bash 不入表，避免误把普通 shell 当 agent。
PROC_MARKERS: Dict[str, str] = {
    "codebuddy":       "codebuddy",
    "openclaw":        "openclaw",
    "hemers":          "hemers",
    "claude":          "claude-code",
    "codex":           "codex",
    "cursor":          "cursor",
    "cursor-electron": "cursor",
    "copilot":         "github-copilot",
    "github-copilot":  "github-copilot",
    "gemini":          "gemini-cli",
    "qwen":            "qwen-code",
    "qwen-code":       "qwen-code",
    "q":               "amazon-q",
    "amazon-q":        "amazon-q",
    "windsurf":        "windsurf",
    "cline":           "cline",
    "roo":             "roo-code",
    "roo-code":        "roo-code",
    "continue":        "continue",
    "aider":           "aider",
    "opencode":        "opencode",
    "openhands":       "openhands",
    "trae":            "trae",
    "kiro":            "kiro",
    "devin":           "devin",
    "replit":          "replit-agent",
}

# 优先级：多个 tag 同时命中时按此顺序取第一个。
CALLER_PRIORITY: List[str] = [
    "codebuddy",
    "openclaw",
    "hemers",
    "claude-code",
    "codex",
    "cursor",
    "github-copilot",
    "gemini-cli",
    "qwen-code",
    "amazon-q",
    "windsurf",
    "cline",
    "roo-code",
    "continue",
    "aider",
    "opencode",
    "openhands",
    "trae",
    "kiro",
    "devin",
    "replit-agent",
]
CALLER_UNKNOWN = "unknown"
CALLER_RAW_SHELL = "raw-shell"
CALLER_DISABLED = "none"
CALLER_WHITELIST: Set[str] = set(CALLER_PRIORITY) | {CALLER_UNKNOWN, CALLER_RAW_SHELL}

CLI_CALLER_HEADER = "X-SkillHub-Caller"
CLI_CALLER_HINT_HEADER = "X-SkillHub-Caller-Hint"
MAX_CALLER_HINT_LEN = 250

# 目录印记向上追溯的最大层数（cwd + 5 层祖先），到达 $HOME 就停。
_CALLER_MAX_DEPTH = 6
# 父进程向上追溯的最大层数。
_CALLER_MAX_PROC_UP = 3


def normalize_cli_client_id(value: Any) -> str:
    text = str(value or "").strip()
    if not text or len(text) > 128:
        return ""
    if not re.fullmatch(r"[A-Za-z0-9._-]+", text):
        return ""
    return text


def resolve_cli_client_config_path() -> Path:
    override = os.environ.get("SKILLHUB_CONFIG_PATH", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(f"{DEFAULT_CLI_HOME}/{CLI_CONFIG_NAME}").expanduser().resolve()


def get_or_create_cli_client_id() -> str:
    global _CLI_CLIENT_ID_CACHE
    if _CLI_CLIENT_ID_CACHE:
        return _CLI_CLIENT_ID_CACHE

    config_path = resolve_cli_client_config_path()
    raw: Dict[str, Any] = {}
    if config_path.exists():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                raw = loaded
        except (json.JSONDecodeError, OSError):
            raw = {}

    existing = normalize_cli_client_id(raw.get(CLI_CLIENT_ID_CONFIG_KEY))
    if existing:
        _CLI_CLIENT_ID_CACHE = existing
        return existing

    client_id = str(uuid.uuid4())
    raw[CLI_CLIENT_ID_CONFIG_KEY] = client_id
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        verbose_log(f"failed to persist CLI client_id: {exc}")
        return ""

    _CLI_CLIENT_ID_CACHE = client_id
    return client_id


# ============================================================
# caller_type 检测实现
# ============================================================


def _read_config_caller_override() -> Optional[str]:
    """从 ~/.skillhub/config.json 读取 caller_override / report_caller_type / 灰度扩表。

    返回：
      - 显式设置的 caller_type（在白名单内）
      - "none" 表示用户永久关闭上报
      - None 表示无 override / 读取失败（静默回退）
    """
    try:
        config_path = resolve_cli_client_config_path()
        if not config_path.exists():
            return None
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(loaded, dict):
        return None

    # 灰度扩表：把 config 里的 dir/env markers merge 到硬编码表之后（用户表覆盖硬编码）
    extra_dirs = loaded.get("caller_dir_markers")
    if isinstance(extra_dirs, dict):
        for name, tag in extra_dirs.items():
            if isinstance(name, str) and isinstance(tag, str) and tag in CALLER_WHITELIST:
                DIR_MARKERS[name] = tag
    extra_envs = loaded.get("caller_env_markers")
    if isinstance(extra_envs, dict):
        for name, tag in extra_envs.items():
            if isinstance(name, str) and isinstance(tag, str) and tag in CALLER_WHITELIST:
                ENV_MARKERS[name] = tag

    # 永久关闭：report_caller_type=false 视同 SKILLHUB_CALLER=none
    if loaded.get("report_caller_type") is False:
        return CALLER_DISABLED

    override = loaded.get("caller_override")
    if isinstance(override, str):
        norm = override.strip().lower()
        if norm in CALLER_WHITELIST or norm == CALLER_DISABLED:
            return norm
    return None


def _pick_by_priority(tags: Set[str]) -> str:
    for t in CALLER_PRIORITY:
        if t in tags:
            return t
    return CALLER_UNKNOWN


def _walk_parent_processes(max_up: int = _CALLER_MAX_PROC_UP) -> List[Tuple[str, str]]:
    """向上遍历父进程链，返回 [(tag, evidence)]。

    优先用 psutil；缺失时 fallback 到 `ps -o comm= -p <pid>`；都不行返回空列表。
    异常一律静默降级，不影响主链路。
    """
    hits: List[Tuple[str, str]] = []
    try:
        pid = os.getppid()
    except OSError:
        return hits

    # 优先 psutil
    try:
        import psutil  # type: ignore
    except ImportError:
        psutil = None  # type: ignore

    if psutil is not None:
        try:
            proc = psutil.Process(pid)
            for _ in range(max_up):
                if proc is None:
                    break
                try:
                    name = (proc.name() or "").lower()
                except Exception:
                    name = ""
                if name:
                    base = os.path.basename(name).lower()
                    tag = PROC_MARKERS.get(base)
                    if tag:
                        hits.append((tag, base))
                try:
                    proc = proc.parent()
                except Exception:
                    break
            return hits
        except Exception:
            hits = []  # psutil 出错则回退到 ps

    # Fallback: 用 ps 遍历（POSIX）；Windows 或 ps 缺失时跳过 L3
    cur_pid = pid
    for _ in range(max_up):
        if cur_pid <= 0:
            break
        try:
            result = subprocess.run(
                ["ps", "-o", "comm=,ppid=", "-p", str(cur_pid)],
                capture_output=True,
                text=True,
                timeout=1,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            break
        if result.returncode != 0:
            break
        line = (result.stdout or "").strip()
        if not line:
            break
        parts = line.split()
        if not parts:
            break
        comm = os.path.basename(parts[0]).lower()
        tag = PROC_MARKERS.get(comm)
        if tag:
            hits.append((tag, comm))
        # 取 ppid 继续向上
        try:
            cur_pid = int(parts[1]) if len(parts) >= 2 else 0
        except ValueError:
            break
    return hits


def _is_interactive_tty() -> bool:
    """stdin / stdout 均为终端时视为交互 shell。"""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except (OSError, ValueError):
        return False


def detect_caller_type() -> Tuple[str, List[str]]:
    """检测本次 CLI 调用的宿主 agent 类型。

    返回 `(caller_type, hint_list)`；异常时降级为 `(unknown, [])`。
    详细决胜矩阵见 tech-design.md §2.4。
    """
    try:
        return _detect_caller_impl()
    except Exception:
        return CALLER_UNKNOWN, ["error"]


def _detect_caller_impl() -> Tuple[str, List[str]]:
    # ─────────── L0: 显式声明 ───────────
    forced = os.environ.get("SKILLHUB_CALLER", "").strip().lower()
    if forced == CALLER_DISABLED:
        return CALLER_DISABLED, []
    if forced in CALLER_WHITELIST:
        return forced, [f"env:SKILLHUB_CALLER={forced}"]

    cfg_forced = _read_config_caller_override()
    if cfg_forced == CALLER_DISABLED:
        return CALLER_DISABLED, []
    if cfg_forced and cfg_forced in CALLER_WHITELIST:
        return cfg_forced, [f"config:{cfg_forced}"]

    # ─────────── L1: 目录印记（区分 project 层 vs $HOME 层） ───────────
    project_tags: Set[str] = set()
    home_tags: Set[str] = set()
    project_hits: List[str] = []
    home_hits: List[str] = []

    try:
        cur = Path.cwd().resolve()
    except (FileNotFoundError, OSError):
        cur = Path("/").resolve()
    try:
        home = Path.home().resolve()
    except (RuntimeError, OSError):
        home = Path("/")

    for depth in range(_CALLER_MAX_DEPTH):
        is_home_level = (cur == home)

        for name, tag in DIR_MARKERS.items():
            try:
                exists = (cur / name).exists()
            except OSError:
                exists = False
            if not exists:
                continue

            entry = f"dir:{name}@depth{depth}:{tag}"
            if is_home_level:
                if tag not in home_tags:
                    home_tags.add(tag)
                    home_hits.append(entry)
            else:
                if tag not in project_tags:
                    project_tags.add(tag)
                    project_hits.append(entry)

        if is_home_level:
            break
        parent = cur.parent
        if parent == cur:
            break
        cur = parent

    # project 层命中 → 强证据，直接决胜
    if project_tags:
        return _pick_by_priority(project_tags), project_hits

    # ─────────── L2: 环境变量印记 ───────────
    env_tags: Set[str] = set()
    env_hits: List[str] = []
    for env_key, tag in ENV_MARKERS.items():
        if env_key in os.environ:
            if tag not in env_tags:
                env_tags.add(tag)
                env_hits.append(f"env:{env_key}:{tag}")

    # 只有 home 层命中时，让 env 参与决胜（有交集取交集，否则取 env）
    if home_tags and env_tags:
        intersect = env_tags & home_tags
        chosen_pool = intersect if intersect else env_tags
        merged_hits = env_hits + home_hits
        return _pick_by_priority(chosen_pool), merged_hits

    if env_tags:
        return _pick_by_priority(env_tags), env_hits

    if home_tags:
        return _pick_by_priority(home_tags), home_hits

    # ─────────── L3: 父进程名 ───────────
    proc_tags: Set[str] = set()
    proc_hits: List[str] = []
    for tag, evidence in _walk_parent_processes(max_up=_CALLER_MAX_PROC_UP):
        if tag not in proc_tags:
            proc_tags.add(tag)
            proc_hits.append(f"proc:{evidence}:{tag}")
    if proc_tags:
        return _pick_by_priority(proc_tags), proc_hits

    # ─────────── 全部未命中 ───────────
    if _is_interactive_tty():
        return CALLER_RAW_SHELL, ["tty:interactive"]
    return CALLER_UNKNOWN, []


@functools.lru_cache(maxsize=1)
def _detect_caller_cached() -> Tuple[str, Tuple[str, ...]]:
    """进程级 LRU cache 版本，一个 CLI 生命周期只跑一次真正检测。

    ⚠️ lru_cache 要求返回值可 hash，因此把 List[str] 转成 tuple。
    调用方按需转回 list。
    """
    caller, hints = detect_caller_type()
    return caller, tuple(hints)


def _reset_detect_caller_cache() -> None:
    """测试专用：清空 caller 检测缓存。生产代码不应调用。"""
    _detect_caller_cached.cache_clear()


def cli_request_headers(headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    out = dict(headers or {})
    out.setdefault("User-Agent", CLI_USER_AGENT)
    client_id = get_or_create_cli_client_id()
    if client_id:
        out.setdefault(CLI_CLIENT_ID_HEADER, client_id)

    # 注入 caller_type / caller_hint（本轮新增）
    try:
        caller_type, caller_hint = _detect_caller_cached()
    except Exception:
        caller_type, caller_hint = CALLER_UNKNOWN, []
    if caller_type and caller_type != CALLER_DISABLED:
        out.setdefault(CLI_CALLER_HEADER, caller_type)
        if caller_hint:
            joined = ",".join(caller_hint)[:MAX_CALLER_HINT_LEN]
            if joined:
                out.setdefault(CLI_CALLER_HINT_HEADER, joined)
    return out


def verbose_enabled() -> bool:
    return os.environ.get("LOG", "") == "VERBOSE"


def verbose_log(message: str) -> None:
    if verbose_enabled():
        print(f"[self-upgrade][verbose] {message}")


def die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    exc = SystemExit(code)
    exc.die_message = message  # type: ignore[attr-defined]
    raise exc


def normalize_file_uri(uri_or_path: str) -> Path:
    parsed = urllib.parse.urlparse(uri_or_path)
    if parsed.scheme == "file":
        # Support:
        # - file:///abs/path
        # - file://localhost/abs/path
        # - file://./relative/path
        if parsed.netloc in ("", "localhost"):
            combined = parsed.path
        else:
            combined = f"{parsed.netloc}{parsed.path}"

        raw_path = urllib.request.url2pathname(combined)
        if not raw_path.strip():
            die(f"Invalid file URI: {uri_or_path}")
        candidate = Path(raw_path).expanduser()
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        return candidate.resolve()
    if parsed.scheme:
        die(f"Only file:// is supported for --index. Got: {uri_or_path}")
    return Path(uri_or_path).expanduser().resolve()


def parse_path_like_uri(uri_or_path: str) -> Path:
    parsed = urllib.parse.urlparse(uri_or_path)
    if parsed.scheme == "file":
        return normalize_file_uri(uri_or_path)
    if parsed.scheme:
        die(f"Only file:// or local paths are supported here. Got: {uri_or_path}")
    return Path(uri_or_path).expanduser().resolve()


def append_slug_zip(base_uri_or_path: str, slug: str) -> str:
    base = base_uri_or_path.strip()
    if not base:
        return ""
    if "{slug}" in base:
        return base.replace("{slug}", urllib.parse.quote(slug))
    parsed = urllib.parse.urlparse(base)
    suffix = f"{urllib.parse.quote(slug)}.zip"
    if parsed.scheme in ("http", "https"):
        return urllib.parse.urljoin(base.rstrip("/") + "/", suffix)
    base_path = parse_path_like_uri(base)
    return (base_path / f"{slug}.zip").resolve().as_uri()


def fill_slug_template(url_template: str, slug: str) -> str:
    raw = str(url_template or "").strip()
    if not raw:
        return ""
    if "{slug}" not in raw:
        return raw
    return raw.replace("{slug}", urllib.parse.quote(slug))


def normalize_namespace_arg(value: Any) -> str:
    return str(value or "").strip().lstrip("@")


def append_query_params(url: str, params: Dict[str, Any]) -> str:
    clean = {
        key: str(value).strip()
        for key, value in params.items()
        if str(value or "").strip()
    }
    if not clean:
        return url
    sep = "&" if urllib.parse.urlparse(url).query else "?"
    return url + sep + urllib.parse.urlencode(clean)


def display_skill_coordinate(slug: str, namespace: str = "") -> str:
    namespace = normalize_namespace_arg(namespace)
    slug = str(slug or "").strip()
    if namespace and slug:
        return f"@{namespace}/{slug}"
    return slug


def read_json_from_uri(uri_or_path: str, timeout: int = 20) -> Dict[str, Any]:
    parsed = urllib.parse.urlparse(uri_or_path)
    if parsed.scheme in ("", "file"):
        path = parse_path_like_uri(uri_or_path)
        if not path.exists():
            raise RuntimeError(f"JSON source not found: {path}")
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSON in {path}: {exc}") from exc
    elif parsed.scheme in ("http", "https"):
        req = urllib.request.Request(
            uri_or_path,
            headers=cli_request_headers({
                "Accept": "application/json",
            }),
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
                raw = json.loads(payload)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Failed to fetch JSON ({exc.code}) from {uri_or_path}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Failed to fetch JSON from {uri_or_path}: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSON from {uri_or_path}: {exc}") from exc
    else:
        raise RuntimeError(f"Unsupported URI scheme for JSON source: {uri_or_path}")

    if not isinstance(raw, dict):
        raise RuntimeError(f"JSON source must be an object: {uri_or_path}")
    return raw


def as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def first_non_empty_string(obj: Dict[str, Any], keys: List[str]) -> str:
    for key in keys:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_version_text(v: str) -> str:
    return v.strip()


def parse_version_key(version: str) -> Optional[Tuple[int, ...]]:
    raw = version.strip().lower()
    if raw.startswith("v"):
        raw = raw[1:]
    if not raw:
        return None
    core = raw.split("-", 1)[0].split("+", 1)[0]
    parts = core.split(".")
    out: List[int] = []
    for part in parts:
        if not part.isdigit():
            return None
        out.append(int(part))
    return tuple(out) if out else None


def version_is_newer(candidate: str, current: str) -> bool:
    candidate = candidate.strip()
    current = current.strip()
    if not candidate:
        return False
    if not current:
        return True
    a = parse_version_key(candidate)
    b = parse_version_key(current)
    if a is not None and b is not None:
        return a > b
    return candidate != current


def parse_bool_like(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("1", "true", "yes", "on"):
            return True
        if normalized in ("0", "false", "no", "off"):
            return False
    return None


def self_update_url_from_config(config: Dict[str, Any]) -> str:
    direct = first_non_empty_string(
        config,
        ["self_update_url", "selfUpdateUrl", "update_url", "updateUrl", "manifest_url", "manifestUrl"],
    )
    if direct:
        return direct

    for key in ("self_update", "selfUpdate", "update", "upgrade"):
        nested = as_dict(config.get(key))
        url_value = first_non_empty_string(nested, ["url", "uri", "manifest", "manifest_url", "manifestUrl"])
        if url_value:
            return url_value
    return ""


def self_update_enabled_from_config(config: Dict[str, Any]) -> Optional[bool]:
    for key in ("auto_self_upgrade", "autoSelfUpgrade", "self_update_auto", "selfUpdateAuto"):
        parsed = parse_bool_like(config.get(key))
        if parsed is not None:
            return parsed

    for key in ("self_update", "selfUpdate", "update", "upgrade"):
        nested = as_dict(config.get(key))
        for nested_key in ("auto", "enabled", "auto_upgrade", "autoUpgrade", "enabled_auto_upgrade"):
            parsed = parse_bool_like(nested.get(nested_key))
            if parsed is not None:
                return parsed
    return None


def resolve_self_update_manifest_url(config_path: Path) -> str:
    if config_path.exists():
        verbose_log(f"reading config: {config_path}")
        try:
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            verbose_log("config JSON invalid; fallback to default manifest URL")
            raw = {}
        if isinstance(raw, dict):
            manifest_url_raw = self_update_url_from_config(raw)
            if manifest_url_raw:
                verbose_log(f"manifest URL from config: {manifest_url_raw}")
                return resolve_uri_with_base(manifest_url_raw, config_path.parent)
    else:
        verbose_log(f"config not found: {config_path}; use default manifest URL")
    verbose_log(f"using default manifest URL: {DEFAULT_SELF_UPDATE_MANIFEST_URL}")
    return DEFAULT_SELF_UPDATE_MANIFEST_URL


def should_run_startup_self_upgrade(config_path: Path) -> bool:
    env_override = parse_bool_like(os.environ.get(SKIP_SELF_UPGRADE_ENV, ""))
    if env_override is True:
        verbose_log(f"startup check skipped by env {SKIP_SELF_UPGRADE_ENV}=true")
        return False
    if not config_path.exists():
        return True
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        verbose_log("startup check: config JSON invalid; keep default auto upgrade")
        return True
    if isinstance(raw, dict):
        enabled = self_update_enabled_from_config(raw)
        if enabled is False:
            verbose_log("startup check skipped by config auto_self_upgrade=false")
            return False
    return True


def find_cli_script_in_extracted(root: Path) -> Optional[Path]:
    direct = root / "skills_store_cli.py"
    if direct.exists():
        return direct
    nested = root / "cli" / "skills_store_cli.py"
    if nested.exists():
        return nested
    matches = list(root.rglob("skills_store_cli.py"))
    return matches[0] if matches else None


def find_peer_file_in_extracted(root: Path, filename: str) -> Optional[Path]:
    direct = root / filename
    if direct.exists():
        return direct
    nested = root / "cli" / filename
    if nested.exists():
        return nested
    matches = list(root.rglob(filename))
    return matches[0] if matches else None


def find_skill_file_in_extracted(root: Path, filename: str) -> Optional[Path]:
    direct = root / "skill" / filename
    if direct.exists():
        return direct
    nested = root / "cli" / "skill" / filename
    if nested.exists():
        return nested
    for match in root.rglob(filename):
        if match.parent.name == "skill":
            return match
    return None


def version_at_least(version: str, minimum: Tuple[int, ...]) -> bool:
    parsed = parse_version_key(version)
    if parsed is None:
        return False
    return parsed >= minimum


def resolve_openclaw_config_path() -> Path:
    override = os.environ.get("OPENCLAW_CONFIG_PATH", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(DEFAULT_OPENCLAW_CONFIG_PATH).expanduser().resolve()


def resolve_skillhub_config_path() -> Path:
    override = os.environ.get("SKILLHUB_CONFIG_PATH", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(f"{DEFAULT_CLI_HOME}/{CLI_CONFIG_NAME}").expanduser().resolve()


def read_json_object(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(raw, dict):
        return {}
    return raw


def should_install_workspace_skills() -> bool:
    env_override = parse_bool_like(os.environ.get(SKIP_WORKSPACE_SKILLS_ENV, ""))
    if env_override is True:
        verbose_log(f"workspace skills install skipped by env {SKIP_WORKSPACE_SKILLS_ENV}=true")
        return False
    if env_override is False:
        return True

    config = read_json_object(resolve_skillhub_config_path())
    configured = parse_bool_like(config.get("install_workspace_skills"))
    if configured is not None:
        return configured
    return True


def openclaw_config_has_skillhub_entry(config: Dict[str, Any]) -> bool:
    plugins = as_dict(config.get("plugins"))
    entries = as_dict(plugins.get("entries"))
    return "skillhub" in entries


def skillhub_plugin_dir_present() -> bool:
    plugin_dir = Path(DEFAULT_OPENCLAW_PLUGIN_DIR).expanduser().resolve()
    if not plugin_dir.exists() or not plugin_dir.is_dir():
        return False
    try:
        next(plugin_dir.iterdir())
        return True
    except StopIteration:
        return False
    except Exception:
        return False


def detect_skillhub_plugin_behavior(config_path: Path) -> Tuple[bool, Dict[str, Any]]:
    config = read_json_object(config_path)
    config_has_entry = openclaw_config_has_skillhub_entry(config)
    plugin_dir_exists = skillhub_plugin_dir_present()
    return plugin_dir_exists or config_has_entry, config


def resolve_openclaw_bin() -> str:
    from_path = shutil.which("openclaw")
    if from_path:
        return from_path
    fallback = Path("~/.local/share/pnpm/openclaw").expanduser().resolve()
    if fallback.exists() and os.access(fallback, os.X_OK):
        return str(fallback)
    return ""


def disable_skillhub_plugin_via_openclaw(openclaw_bin: str) -> bool:
    if not openclaw_bin:
        return False
    try:
        result = subprocess.run(
            [openclaw_bin, "config", "unset", "plugins.entries.skillhub"],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:
        verbose_log(f"disable plugin by openclaw failed: {exc}")
        return False
    if result.returncode == 0:
        verbose_log("removed skillhub plugin config via openclaw config unset")
        return True
    err = (result.stderr or result.stdout or "").strip()
    if "config path not found" in err.lower():
        verbose_log("skillhub plugin config already absent")
        return True
    if err:
        verbose_log(f"openclaw config unset failed: {err}")
    return False


def resolve_openclaw_workspace_path(config: Dict[str, Any]) -> Path:
    env_workspace = os.environ.get("OPENCLAW_WORKSPACE", "").strip()
    if env_workspace:
        return Path(env_workspace).expanduser().resolve()

    for key in ("workspace", "workspace_dir", "workspaceDir", "workspace_path", "workspacePath"):
        value = config.get(key)
        if isinstance(value, str) and value.strip():
            return Path(value.strip()).expanduser().resolve()

    paths = as_dict(config.get("paths"))
    for key in ("workspace", "workspaceDir", "workspace_path", "workspacePath"):
        value = paths.get(key)
        if isinstance(value, str) and value.strip():
            return Path(value.strip()).expanduser().resolve()

    return Path(DEFAULT_OPENCLAW_WORKSPACE_PATH).expanduser().resolve()


def read_skill_template(template_path: Optional[Path]) -> str:
    if template_path and template_path.exists():
        try:
            content = template_path.read_text(encoding="utf-8").strip()
            if content:
                return content
        except Exception:
            pass
    return ""


def install_workspace_skill(workspace_path: Path, slug: str, content: str) -> Path:
    target = workspace_path / "skills" / slug / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = content if content.endswith("\n") else (content + "\n")
    target.write_text(payload, encoding="utf-8")
    return target


def run_post_upgrade_plugin_migration(
    latest_version: str,
    find_skill_template: Optional[Path],
    preference_skill_template: Optional[Path],
) -> None:
    # This migration belongs to the OTA self-upgrade path and runs only after
    # a successful CLI upgrade.
    if not version_at_least(latest_version, POST_UPGRADE_SKILL_MIGRATION_MIN_VERSION):
        verbose_log(f"post-upgrade migration skipped; version<{POST_UPGRADE_SKILL_MIGRATION_MIN_VERSION}")
        return

    config_path = resolve_openclaw_config_path()
    has_plugin_behavior, config = detect_skillhub_plugin_behavior(config_path)
    if not has_plugin_behavior:
        verbose_log("post-upgrade migration skipped; no skillhub plugin behavior detected")
        return

    verbose_log("skillhub plugin behavior detected; run migration to workspace skills")
    openclaw_bin = resolve_openclaw_bin()
    disabled = disable_skillhub_plugin_via_openclaw(openclaw_bin) if openclaw_bin else False

    if not disabled:
        verbose_log("skip plugin-disable fallback; openclaw command unavailable or failed")

    if not should_install_workspace_skills():
        verbose_log("workspace skills install disabled by config/env; skip install")
        return

    config_after = read_json_object(config_path)
    workspace_path = resolve_openclaw_workspace_path(config_after if config_after else config)
    # Template sources are package files in plain text:
    # skill/SKILL.md and skill/SKILL.skillhub-preference.md.
    find_skill_text = read_skill_template(find_skill_template)
    preference_skill_text = read_skill_template(preference_skill_template)

    if find_skill_text:
        find_target = install_workspace_skill(workspace_path, FIND_SKILLS_SLUG, find_skill_text)
        verbose_log(f"installed migrated skill: {find_target}")
    else:
        verbose_log("find-skills template missing in package; skip install")

    if preference_skill_text:
        preference_target = install_workspace_skill(
            workspace_path,
            SKILLHUB_PREFERENCE_SLUG,
            preference_skill_text,
        )
        verbose_log(f"installed migrated skill: {preference_target}")
    else:
        verbose_log("skillhub-preference template missing in package; skip install")


def resolve_uri_with_base(raw: str, base_dir: Path) -> str:
    value = raw.strip()
    if not value:
        return ""
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme in ("http", "https"):
        return value
    if parsed.scheme == "file":
        return parse_path_like_uri(value).as_uri()
    if parsed.scheme != "":
        die(f"Unsupported URI scheme: {value}")
    return (base_dir / value).resolve().as_uri()


def extract_update_manifest_info(manifest: Dict[str, Any]) -> Tuple[str, str, str]:
    candidates = [manifest]
    for key in ("latest", "release", "data", "skill", "package"):
        nested = manifest.get(key)
        if isinstance(nested, dict):
            candidates.append(nested)

    latest_version = ""
    package_uri = ""
    sha256 = ""
    for item in candidates:
        if not latest_version:
            latest_version = first_non_empty_string(item, ["version", "latest_version", "latestVersion"])
        if not package_uri:
            package_uri = first_non_empty_string(
                item,
                ["zip_url", "zipUrl", "download_url", "downloadUrl", "package_url", "packageUrl", "url"],
            )
        if not sha256:
            sha256 = first_non_empty_string(item, ["sha256", "sha_256", "checksum"])
    return latest_version, package_uri, sha256.lower()


def install_zip_to_target(
    slug: str,
    zip_uri: str,
    target_dir: Path,
    force: bool,
    expected_sha256: str = "",
) -> None:
    if target_dir.exists() and not force:
        die(f"Target exists: {target_dir} (use --force to overwrite)")

    with tempfile.TemporaryDirectory(prefix="skills-store-cli-") as tmp:
        zip_path = Path(tmp) / f"{slug}.zip"
        stage_dir = Path(tmp) / "stage"
        stage_dir.mkdir(parents=True, exist_ok=True)
        print(f"Downloading: {zip_uri}", file=sys.stderr)
        download_file(zip_uri, zip_path)

        if expected_sha256:
            actual_sha256 = sha256_file(zip_path).lower()
            if actual_sha256 != expected_sha256:
                die(
                    f"SHA256 mismatch for {slug}: expected {expected_sha256}, got {actual_sha256}"
                )
        try:
            safe_extract_zip(zip_path, stage_dir)
        except zipfile.BadZipFile:
            die(f"Downloaded file is not a valid zip archive: {zip_uri}")

        if target_dir.exists():
            if not force:
                die(f"Target exists: {target_dir} (use --force to overwrite)")
            shutil.rmtree(target_dir)
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(stage_dir), str(target_dir))


def install_zip_to_target_with_fallback(
    slug: str,
    zip_uris: List[str],
    target_dir: Path,
    force: bool,
    expected_sha256: str = "",
    quiet: bool = False,
) -> None:
    candidates = [str(x).strip() for x in zip_uris if str(x).strip()]
    seen = set()
    ordered: List[str] = []
    for x in candidates:
        if x in seen:
            continue
        seen.add(x)
        ordered.append(x)
    if not ordered:
        die(f'No download URL candidates for "{slug}"')

    if target_dir.exists() and not force:
        die(f"Target exists: {target_dir} (use --force to overwrite)")

    with tempfile.TemporaryDirectory(prefix="skills-store-cli-") as tmp:
        zip_path = Path(tmp) / f"{slug}.zip"
        stage_dir = Path(tmp) / "stage"
        stage_dir.mkdir(parents=True, exist_ok=True)
        last_err = ""
        used_uri = ""
        for idx, zip_uri in enumerate(ordered):
            try:
                if not quiet:
                    print(f"Downloading: {zip_uri}", file=sys.stderr)
                download_file_or_raise(zip_uri, zip_path)
                used_uri = zip_uri
                last_err = ""
                break
            except Exception as exc:
                last_err = str(exc)
                if idx + 1 < len(ordered):
                    if not quiet:
                        print(f"Download failed, fallback next source: {exc}", file=sys.stderr)
                    continue
        if last_err:
            die(last_err)

        if expected_sha256:
            actual_sha256 = sha256_file(zip_path).lower()
            if actual_sha256 != expected_sha256:
                die(
                    f"SHA256 mismatch for {slug}: expected {expected_sha256}, got {actual_sha256}"
                )
        try:
            safe_extract_zip(zip_path, stage_dir)
        except zipfile.BadZipFile:
            die(f"Downloaded file is not a valid zip archive: {used_uri or ordered[0]}")

        if target_dir.exists():
            if not force:
                die(f"Target exists: {target_dir} (use --force to overwrite)")
            shutil.rmtree(target_dir)
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(stage_dir), str(target_dir))


def normalize_skills_payload(data: Any) -> Dict[str, Any]:
    if isinstance(data, dict):
        skills = data.get("skills")
        if isinstance(skills, list):
            return data
        die('Index JSON must include a "skills" array.')
    if isinstance(data, list):
        return {"skills": data}
    die("Index JSON must be an object or array.")
    return {"skills": []}


def load_index(index_uri: str) -> Dict[str, Any]:
    try:
        data = read_json_from_uri(index_uri, timeout=20)
    except Exception as exc:
        die(str(exc))
    return normalize_skills_payload(data)


def index_local_path_or_none(index_uri: str) -> Optional[Path]:
    parsed = urllib.parse.urlparse(index_uri)
    if parsed.scheme in ("", "file"):
        return parse_path_like_uri(index_uri)
    return None


def skill_zip_uri(
    skill: Dict[str, Any],
    slug: str,
    index_path: Optional[Path],
    files_base_uri: str,
    download_url_template: str,
) -> str:
    if files_base_uri.strip():
        from_base = append_slug_zip(files_base_uri, slug)
        if from_base:
            return from_base

    if index_path is not None:
        sibling_files = (index_path.parent / "files" / f"{slug}.zip").resolve()
        if sibling_files.exists():
            return sibling_files.as_uri()

    for key in ("zip_url", "zipUrl", "archive_url", "archiveUrl", "file_url", "fileUrl"):
        raw = str(skill.get(key, "")).strip()
        if raw:
            if urllib.parse.urlparse(raw).scheme:
                return raw
            return Path(raw).expanduser().resolve().as_uri()

    if download_url_template.strip():
        return append_slug_zip(download_url_template, slug)

    die(
        f'Skill "{slug}" has no zip_url and no local archive found. '
        "Use --files-base-uri or --download-url-template."
    )
    return ""


def load_lockfile(install_root: Path) -> Dict[str, Any]:
    lock_path = install_root / LOCKFILE_NAME
    if not lock_path.exists():
        return {"version": 1, "skills": {}}
    try:
        raw = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "skills": {}}
    if not isinstance(raw, dict):
        return {"version": 1, "skills": {}}
    if not isinstance(raw.get("skills"), dict):
        raw["skills"] = {}
    return raw


def save_lockfile(install_root: Path, lock: Dict[str, Any]) -> None:
    install_root.mkdir(parents=True, exist_ok=True)
    lock_path = install_root / LOCKFILE_NAME
    lock_path.write_text(json.dumps(lock, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve_clawhub_lock_path() -> Path:
    override = os.environ.get("SKILLHUB_CLAWHUB_LOCK_PATH", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path("~/.openclaw/workspace/.clawhub/lock.json").expanduser().resolve()


def update_clawhub_lock_v1(slug: str, version: str) -> None:
    lock_path = resolve_clawhub_lock_path()
    if not lock_path.exists():
        verbose_log(f"clawhub lock not found, skip sync: {lock_path}")
        return
    try:
        raw = json.loads(lock_path.read_text(encoding="utf-8"))
    except Exception:
        verbose_log(f"clawhub lock invalid JSON, skip sync: {lock_path}")
        return
    if not isinstance(raw, dict) or raw.get("version") != 1:
        verbose_log(f"clawhub lock version is not 1, skip sync: {lock_path}")
        return
    skills = raw.get("skills")
    if not isinstance(skills, dict):
        skills = {}
        raw["skills"] = skills
    skills[slug] = {
        "version": version,
        "installedAt": int(time.time() * 1000),
    }
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        verbose_log(f"synced clawhub lock entry: {slug} -> {lock_path}")
    except Exception:
        verbose_log(f"failed to write clawhub lock, skip: {lock_path}")


def skill_text(skill: Dict[str, Any]) -> str:
    tags = skill.get("tags") or []
    if not isinstance(tags, list):
        tags = []
    categories = skill.get("categories") or []
    if not isinstance(categories, list):
        categories = []
    text = " ".join(
        [
            str(skill.get("slug", "")),
            str(skill.get("name", "")),
            str(skill.get("description", "")),
            str(skill.get("summary", "")),
            str(skill.get("version", "")),
            " ".join(str(tag) for tag in tags),
            " ".join(str(category) for category in categories),
        ]
    )
    return text.lower()



# ============================================================
# Enterprise Credentials Management
# ============================================================

CREDENTIALS_FILE_NAME = "credentials.json"
DEFAULT_ENTERPRISE_HOST = "https://api.skillhub.cn"
ENTERPRISE_VERIFY_TIMEOUT = 10
ENTERPRISE_SEARCH_TIMEOUT = 3


def get_credentials_path() -> Path:
    """返回凭证文件路径: ~/.skillhub/credentials.json"""
    return Path(DEFAULT_CLI_HOME).expanduser() / CREDENTIALS_FILE_NAME


def load_credentials() -> Dict[str, Any]:
    """加载凭证文件，返回完整 JSON 对象。不存在则返回空结构。"""
    cred_path = get_credentials_path()
    if not cred_path.exists():
        return {"version": 1, "orgs": {}}
    try:
        raw = json.loads(cred_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return {"version": 1, "orgs": {}}
        if "orgs" not in raw or not isinstance(raw["orgs"], dict):
            raw["orgs"] = {}
        return raw
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "orgs": {}}


def save_credentials(creds: Dict[str, Any]) -> None:
    """原子写入凭证文件（先写临时文件再 rename），权限 0600。"""
    cred_path = get_credentials_path()
    cred_path.parent.mkdir(parents=True, exist_ok=True)
    # 原子写入
    tmp_path = cred_path.with_suffix(".tmp")
    try:
        tmp_path.write_text(json.dumps(creds, indent=2, ensure_ascii=False), encoding="utf-8")
        os.chmod(str(tmp_path), 0o600)
        tmp_path.replace(cred_path)
    except OSError:
        # fallback: 直接写
        cred_path.write_text(json.dumps(creds, indent=2, ensure_ascii=False), encoding="utf-8")
        try:
            os.chmod(str(cred_path), 0o600)
        except OSError:
            pass


def get_org_credential(org_slug: str) -> Optional[Dict[str, Any]]:
    """获取指定 org 的凭证信息。

    支持按团队 ID（orgOrgId，不可变）或英文简称（orgSlug，可变）匹配。
    优先精确匹配 key（团队 ID），失败后 fallback 按 orgSlug 或 orgOrgId 字段遍历匹配。
    """
    creds = load_credentials()
    orgs = creds.get("orgs", {})
    # 1. 精确匹配 key（团队 ID）
    if org_slug in orgs:
        return orgs[org_slug]
    # 2. Fallback: 遍历所有凭证，按 orgOrgId 或 orgSlug 字段匹配
    for _key, info in orgs.items():
        if info.get("orgOrgId") == org_slug or info.get("orgSlug") == org_slug:
            return info
    return None


def get_all_org_credentials() -> Dict[str, Dict[str, Any]]:
    """获取所有已登录的 org 凭证，按 loggedInAt 倒序排列。"""
    creds = load_credentials()
    orgs = creds.get("orgs", {})
    # 按 loggedInAt 倒序排列
    sorted_orgs = dict(
        sorted(orgs.items(), key=lambda x: x[1].get("loggedInAt", ""), reverse=True)
    )
    return sorted_orgs


def resolve_org_credential_from_env() -> Optional[Dict[str, Any]]:
    """从环境变量解析企业凭证（CI/CD 场景），优先级高于 credentials.json。"""
    org_slug = os.environ.get("SKILLHUB_ORG", "").strip()
    api_key = os.environ.get("SKILLHUB_API_KEY", "").strip()
    if not org_slug or not api_key:
        return None
    host = os.environ.get("SKILLHUB_HOST", "").strip() or DEFAULT_ENTERPRISE_HOST
    return {
        "orgOrgId": org_slug,
        "orgSlug": org_slug,
        "host": host,
        "apiKey": api_key,
        "fromEnv": True,
    }


def mask_api_key(key: str) -> str:
    """脱敏展示 API Key: sk-ent-b0df...cec0"""
    if len(key) <= 15:
        return key[:4] + "..." + key[-4:] if len(key) > 8 else "***"
    return key[:11] + "..." + key[-4:]


def parse_skill_ref(ref: str) -> Tuple[Optional[str], str, Optional[str]]:
    """Parse a skill reference like '@org/slug@version' into (org, slug, version).

    Examples:
        'my-skill'           -> (None, 'my-skill', None)
        '@tencent/my-skill'  -> ('tencent', 'my-skill', None)
        '@tencent/my-skill@1.0.0' -> ('tencent', 'my-skill', '1.0.0')
    """
    org: Optional[str] = None
    version: Optional[str] = None
    if ref.startswith("@"):
        parts = ref[1:].split("/", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(f"Invalid skill reference: {ref}. Expected format: @org/slug")
        org = parts[0]
        ref = parts[1]
    if "@" in ref:
        ref, version = ref.rsplit("@", 1)
    if not ref:
        raise ValueError(f"Invalid skill reference: slug cannot be empty")
    return org, ref, version


def verify_api_key(host: str, api_key: str) -> Dict[str, Any]:
    """调用 POST {host}/api/v1/registry/verify 验证 API Key，返回 org 信息。

    Returns: {"orgId": int, "orgOrgId": str, "orgSlug": str, "orgName": str}
    Raises: RuntimeError on failure.
    """
    url = f"{host.rstrip('/')}/api/v1/registry/verify"
    req = urllib.request.Request(
        url,
        method="POST",
        headers=cli_request_headers({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }),
        data=b"",
    )
    try:
        with urllib.request.urlopen(req, timeout=ENTERPRISE_VERIFY_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            if not isinstance(body, dict) or "orgId" not in body:
                raise RuntimeError("Unexpected response from verify endpoint")
            return body
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            try:
                err_body = json.loads(exc.read().decode("utf-8"))
                msg = err_body.get("error", "invalid or expired API key")
            except Exception:
                msg = "invalid or expired API key"
            raise RuntimeError(msg)
        raise RuntimeError(f"Verify request failed (HTTP {exc.code})")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Cannot connect to {host}: {exc.reason}")
    except Exception as exc:
        raise RuntimeError(f"Verify request failed: {exc}")


def fetch_enterprise_search_results(
    host: str,
    org_id: int,
    api_key: str,
    query: str,
    limit: int = 20,
) -> Optional[List[Dict[str, Any]]]:
    """搜索企业源技能，返回结果列表。超时或失败返回 None。"""
    url = f"{host.rstrip('/')}/api/v1/orgs/{org_id}/registry/search"
    params = urllib.parse.urlencode({"q": query, "pageSize": limit})
    full_url = f"{url}?{params}"
    req = urllib.request.Request(
        full_url,
        headers=cli_request_headers({
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }),
    )
    try:
        with urllib.request.urlopen(req, timeout=ENTERPRISE_SEARCH_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            if not isinstance(body, dict):
                return None
            skills = body.get("skills", [])
            if not isinstance(skills, list):
                return None
            return skills
    except Exception:
        return None


def download_enterprise_skill(
    host: str,
    org_id: int,
    api_key: str,
    slug: str,
    version: Optional[str],
    target_dir: Path,
    force: bool = False,
) -> Optional[str]:
    """下载企业技能 ZIP 并解压到 target_dir。返回版本号或 None（失败）。"""
    url = f"{host.rstrip('/')}/api/v1/orgs/{org_id}/registry/skills/{slug}/download"
    if version:
        url += f"?version={urllib.parse.quote(version)}"

    req = urllib.request.Request(
        url,
        headers=cli_request_headers({
            "Authorization": f"Bearer {api_key}",
        }),
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            # 跟随重定向后获取最终内容
            content = resp.read()
            # 从 Content-Disposition 或 URL 提取版本号
            cd = resp.headers.get("Content-Disposition", "")
            detected_version = version or ""
            if not detected_version and cd:
                # filename="slug-1.0.0.zip"
                import re
                m = re.search(r'filename="?([^"]+)"?', cd)
                if m:
                    fname = m.group(1)
                    if fname.startswith(slug + "-") and fname.endswith(".zip"):
                        detected_version = fname[len(slug) + 1:-4]

            # 写入临时文件并解压
            if target_dir.exists() and not force:
                shutil.rmtree(target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            try:
                with zipfile.ZipFile(tmp_path, "r") as zf:
                    zf.extractall(target_dir)
            finally:
                os.unlink(tmp_path)

            return detected_version or "latest"
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise RuntimeError(f"Download failed (HTTP {exc.code})")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Cannot connect to {host}: {exc.reason}")


def normalize_source_label(value: Any) -> str:
    source = str(value or "").strip()
    if not source or source.lower() == "unknown":
        return "skillhub"
    return source


def is_clawhub_url(value: str) -> bool:
    try:
        host = urllib.parse.urlparse(value).netloc.lower()
    except Exception:
        return False
    return host == "clawhub.ai" or host.endswith(".clawhub.ai")


def fetch_remote_search_results(
    search_url: str,
    query: str,
    limit: int,
    timeout: int,
) -> Optional[List[Dict[str, Any]]]:
    base = str(search_url or "").strip()
    q = str(query or "").strip()
    if not base or not q:
        return None
    try:
        parsed = urllib.parse.urlparse(base)
        if parsed.scheme not in ("http", "https"):
            return None
        params = urllib.parse.urlencode({"q": q, "limit": max(1, int(limit))})
        full_url = urllib.parse.urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path, parsed.params, params, parsed.fragment)
        )
        req = urllib.request.Request(
            full_url,
            headers=cli_request_headers({
                "Accept": "application/json",
            }),
        )
        with urllib.request.urlopen(req, timeout=max(1, int(timeout))) as response:
            payload = response.read().decode("utf-8")
        raw = json.loads(payload)
        if not isinstance(raw, dict):
            return None
        results = raw.get("results")
        if not isinstance(results, list):
            return None
        out: List[Dict[str, Any]] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            slug = str(item.get("slug", "")).strip()
            if not slug:
                continue
            out.append(
                {
                    "slug": slug,
                    "name": str(item.get("displayName") or item.get("name") or slug).strip() or slug,
                    "description": str(item.get("summary") or item.get("description") or "").strip(),
                    "summary": str(item.get("summary") or "").strip(),
                    "version": str(item.get("version") or "").strip(),
                    "namespace": item.get("namespace") if isinstance(item.get("namespace"), dict) else None,
                }
            )
        return out
    except Exception:
        return None


def cmd_search(args: argparse.Namespace) -> None:
    query_parts = args.query if isinstance(args.query, list) else [args.query]
    query = " ".join(str(part) for part in query_parts).lower().strip()
    json_out = bool(getattr(args, "json_output", False))
    scope_org = getattr(args, "org", None)
    if scope_org:
        scope_org = scope_org.strip()

    if not query:
        # 无查询词时，展示本地 index（保持原有行为）
        _search_local_index(args, query, json_out)
        return

    # 联合搜索: 企业源 + 社区源
    warnings: List[str] = []
    enterprise_results: List[Dict[str, Any]] = []
    community_results: List[Dict[str, Any]] = []

    # 1. 搜索企业源（所有已登录的，或仅指定的 --org）
    if not scope_org or scope_org != "community":
        orgs = get_all_org_credentials()
        if scope_org:
            # 仅搜索指定企业源（支持按 key、orgOrgId 或 orgSlug 匹配）
            if scope_org in orgs:
                orgs = {scope_org: orgs[scope_org]}
            else:
                # Fallback: 按 orgOrgId 或 orgSlug 字段遍历匹配
                matched = {k: v for k, v in orgs.items()
                           if v.get("orgOrgId") == scope_org or v.get("orgSlug") == scope_org}
                if matched:
                    orgs = matched
                else:
                    warnings.append(f"@{scope_org}: not logged in, skipped")
                    orgs = {}

        for org_slug, cred in orgs.items():
            host = cred.get("host", DEFAULT_ENTERPRISE_HOST)
            org_id = cred.get("orgId")
            api_key = cred.get("apiKey", "")
            if not org_id or not api_key:
                continue
            results = fetch_enterprise_search_results(
                host=host,
                org_id=org_id,
                api_key=api_key,
                query=query,
                limit=args.search_limit,
            )
            if results is None:
                warnings.append(f"@{org_slug}: request timed out or failed, results omitted")
            elif results:
                for skill in results:
                    skill["_source"] = f"@{org_slug}"
                    skill["_org"] = org_slug
                enterprise_results.extend(results)

    # 2. 搜索社区源（除非 --org 指定了企业源）
    if not scope_org or scope_org == "community":
        community = fetch_remote_search_results(
            search_url=args.search_url,
            query=query,
            limit=args.search_limit,
            timeout=args.search_timeout,
        )
        if community is not None:
            for skill in community:
                skill["_source"] = "community"
            community_results = community
        elif not scope_org:
            warnings.append("community: search request failed")

    # 3. 合并结果: 企业源优先
    all_results = enterprise_results + community_results

    # 4. 打印警告
    for w in warnings:
        print(f"\u26a0\ufe0f  {w}", file=sys.stderr)

    if not all_results:
        print("No skills found.")
        return

    # 5. 输出
    if json_out:
        output_results = []
        for skill in all_results:
            source = skill.get("_source", "community")
            raw_slug = skill.get("slug", "")
            # 企业源展示 @org/slug 格式，与非 JSON 模式一致
            if source.startswith("@"):
                display_slug = f"@{skill.get('_org', '')}/{raw_slug}"
            else:
                ns = skill.get("namespace") if isinstance(skill.get("namespace"), dict) else {}
                display_slug = str(ns.get("canonicalName") or raw_slug)
            output_results.append({
                "slug": display_slug,
                "publicSlug": raw_slug,
                "name": skill.get("name") or skill.get("displayName", ""),
                "description": skill.get("description") or skill.get("summary", ""),
                "version": skill.get("version", ""),
                "source": source,
                "namespace": skill.get("namespace") if isinstance(skill.get("namespace"), dict) else None,
            })
        print(
            json.dumps(
                {
                    "query": query,
                    "count": len(output_results),
                    "results": output_results,
                    "warnings": warnings,
                },
                ensure_ascii=False,
            )
        )
        return

    print('You can use "skillhub install [skill]" to install.')
    for skill in all_results:
        source = skill.get("_source", "community")
        slug = skill.get("slug", "<unknown>")
        name = skill.get("name") or skill.get("displayName", slug)
        description = skill.get("description") or skill.get("summary", "")
        version = skill.get("version", "")
        # 企业源展示 @org/slug 格式，社区源直接展示 slug
        if source.startswith("@"):
            display_slug = f"@{skill.get('_org', '')}/{slug}"
        else:
            ns = skill.get("namespace") if isinstance(skill.get("namespace"), dict) else {}
            display_slug = str(ns.get("canonicalName") or slug)
        print(f"  {display_slug}  {name}")
        if description:
            print(f"    - {description}")
        if version:
            print(f"    - version: {version}")
        ns = skill.get("namespace") if isinstance(skill.get("namespace"), dict) else {}
        if not source.startswith("@") and ns.get("handle"):
            print(f"    - install: skillhub install {slug} --namespace {ns['handle']}")


def _search_local_index(args: argparse.Namespace, query: str, json_out: bool) -> None:
    """搜索本地 index（无查询词时的 fallback）。"""
    data = load_index(args.index)
    matches: List[Dict[str, Any]] = []
    for item in data["skills"]:
        if not isinstance(item, dict):
            continue
        matches.append(item)

    if not matches:
        print("No skills found.")
        return

    if query:
        def rank(skill: Dict[str, Any]) -> Tuple[int, str]:
            text = skill_text(skill)
            score = text.count(query)
            slug = str(skill.get("slug", ""))
            return (score, slug)

        matches.sort(key=rank, reverse=True)

    if json_out:
        results: List[Dict[str, Any]] = []
        for skill in matches:
            if not isinstance(skill, dict):
                continue
            slug = str(skill.get("slug") or "").strip()
            if not slug:
                continue
            name = str(skill.get("name") or skill.get("displayName") or slug).strip() or slug
            description = str(skill.get("description") or skill.get("summary") or "").strip()
            version = str(skill.get("version") or "").strip()
            results.append(
                {
                    "slug": slug,
                    "name": name,
                    "description": description,
                    "summary": str(skill.get("summary") or "").strip(),
                    "version": version,
                    "source": "community",
                    "namespace": skill.get("namespace") if isinstance(skill.get("namespace"), dict) else None,
                }
            )
        print(
            json.dumps(
                {
                    "query": query,
                    "count": len(results),
                    "results": results,
                },
                ensure_ascii=False,
            )
        )
        return

    print('You can use "skillhub install [skill]" to install.')

    for skill in matches:
        slug = skill.get("slug", "<unknown>")
        name = skill.get("name", slug)
        description = skill.get("description", "")
        if not description:
            description = skill.get("summary", "")
        zip_url = skill.get("zip_url", "")
        homepage = skill.get("homepage", "")
        version = skill.get("version", "")
        print(f"  {slug}  {name}")
        if description:
            print(f"    - {description}")
        if version:
            print(f"    - version: {version}")
        if zip_url:
            print(f"    - {zip_url}")
        if homepage and not is_clawhub_url(homepage):
            print(f"    - {homepage}")


def download_file_or_raise(url: str, dest: Path) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == "file":
        source_path = parse_path_like_uri(url)
        if not source_path.exists():
            raise RuntimeError(f"Download failed: local file not found: {source_path}")
        shutil.copyfile(source_path, dest)
        return
    if parsed.scheme == "":
        source_path = Path(url).expanduser().resolve()
        if source_path.exists():
            shutil.copyfile(source_path, dest)
            return

    req = urllib.request.Request(
        url,
        headers=cli_request_headers({
            "Accept": "application/zip,application/octet-stream,*/*",
        }),
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status and response.status >= 400:
                raise RuntimeError(f"Download failed ({response.status}) for {url}")
            with dest.open("wb") as out:
                shutil.copyfileobj(response, out)
    except urllib.error.HTTPError as exc:
        detail = f"HTTP {exc.code}"
        if exc.code == 429:
            detail += " (rate limited)"
        raise RuntimeError(f"Download failed: {detail} for {url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Download failed: {exc.reason} for {url}") from exc


def download_file(url: str, dest: Path) -> None:
    try:
        download_file_or_raise(url, dest)
    except Exception as exc:
        die(str(exc))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_extract_zip(zip_path: Path, target_dir: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = Path(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                die(f"Unsafe zip path entry detected: {member.filename}")
        zf.extractall(target_dir)


def safe_extract_tar(tar_path: Path, target_dir: Path) -> None:
    with tarfile.open(tar_path, "r:*") as tf:
        for member in tf.getmembers():
            member_path = Path(member.name)
            if member_path.is_absolute() or ".." in member_path.parts:
                die(f"Unsafe tar path entry detected: {member.name}")
        try:
            tf.extractall(target_dir, filter="data")
        except TypeError:
            tf.extractall(target_dir)


def find_skill(data: Dict[str, Any], slug: str) -> Optional[Dict[str, Any]]:
    for item in data["skills"]:
        if isinstance(item, dict) and str(item.get("slug", "")).strip() == slug:
            return item
    return None


# ============================================================
# User API Token (skh_) — credentials helpers
#
# 历史：早期曾基于 user_api_keys 表 + sh_pat_ 前缀做独立 PAT 体系，
# 2026-06-08 决策回滚，统一改用更早的 skh_ API Token。
# 设计差异：
#   - skh_ 永久有效、无 scope、无每用户上限；
#   - 安全防护完全靠后端 publish 接口的多维度限流（按 token / IP）。
# ============================================================


def load_user_credential() -> Optional[Dict[str, Any]]:
    """读取 ~/.skillhub/credentials.json::user 节点。

    返回 dict 含 keys: host, token, userId, handle, loggedInAt；不存在时返回 None。
    不破坏 orgs 字段。
    """
    creds = load_credentials()
    user = creds.get("user")
    if not isinstance(user, dict):
        return None
    if not user.get("token"):
        return None
    return user


def save_user_credential(host: str, token: str, user_id: int, handle: str) -> None:
    """写入 user 字段；保留 orgs 与其他字段。"""
    creds = load_credentials()
    creds.setdefault("orgs", {})
    creds["user"] = {
        "host": host,
        "token": token,
        "userId": int(user_id),
        "handle": handle,
        "loggedInAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    save_credentials(creds)


def clear_user_credential() -> None:
    """删除 user 字段；保留 orgs。"""
    creds = load_credentials()
    if "user" in creds:
        del creds["user"]
        save_credentials(creds)


def resolve_user_token(args: argparse.Namespace) -> Tuple[str, str]:
    """解析当前调用使用的 API Token (skh_) 与 host。

    优先级：--token > SKILLHUB_TOKEN env > credentials.json::user.token。
    返回 (token, host)；任何缺失 → die(...)。
    """
    token = (getattr(args, "token", None) or "").strip()
    host = (getattr(args, "host", None) or "").strip()
    env_token = os.environ.get("SKILLHUB_TOKEN", "").strip()
    if not token:
        token = env_token
    cred = load_user_credential()
    if not token and cred:
        token = (cred.get("token") or "").strip()
    if not host:
        if cred and cred.get("host"):
            host = str(cred["host"]).strip()
        else:
            host = os.environ.get("SKILLHUB_API_BASE", "").strip() or DEFAULT_ENTERPRISE_HOST
    if not token:
        die("未登录。请先执行: skillhub login --key skh_xxx")
    if not token.startswith("skh_"):
        die("token 必须以 skh_ 开头（早期 sh_pat_ 体系已下线）")
    return token, host


# ============================================================
# User API Token — auth subcommands
# ============================================================


def _get_auth_me(host: str, token: str, *, timeout: int = 10) -> Dict[str, Any]:
    """调用 GET /api/v1/auth/me 验证 token 合法性，返回响应 JSON。

    用作 whoami 的后端实现。失败时抛出 RuntimeError。
    """
    url = host.rstrip("/") + "/api/v1/auth/me"
    req = urllib.request.Request(
        url,
        method="GET",
        headers=cli_request_headers({
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }),
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - 仅访问用户配置的 host
            body = resp.read()
            try:
                return json.loads(body.decode("utf-8") or "{}")
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"auth/me 响应非合法 JSON: {exc}") from exc
    except urllib.error.HTTPError as exc:
        body_bytes = b""
        try:
            body_bytes = exc.read() or b""
        except Exception:
            body_bytes = b""
        snippet = body_bytes.decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"HTTP {exc.code}: {snippet}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"网络错误: {exc.reason}") from exc


def cmd_auth_login(args: argparse.Namespace) -> None:
    """skillhub login --key skh_xxx [--host https://api.skillhub.cn]

    兼容旧命令：skillhub auth login --token skh_xxx [--host ...]

    通过 GET /api/v1/auth/me 校验 token 合法性，校验通过才写入 credentials.json::user。
    """
    token = (args.token or "").strip()
    if not token:
        die("--token 不能为空")
    if not token.startswith("skh_"):
        die("--token 必须以 skh_ 开头（早期 sh_pat_ 体系已下线）")
    host = (args.host or "").strip() or DEFAULT_ENTERPRISE_HOST
    try:
        info = _get_auth_me(host, token)
    except RuntimeError as exc:
        die(f"登录失败: {exc}")
    # /api/v1/auth/me 返回结构（现网当前）：{ "user": { id, handle, role, ... } }
    # 兼容性：
    #   1) 早期 whoami 直接返回 { id, handle, ... } 平铺结构
    #   2) 早期字段名为 userId
    #   3) 现网包了一层 { "user": {...} }
    user_payload = info.get("user") if isinstance(info.get("user"), dict) else info
    user_id = user_payload.get("id") or user_payload.get("userId")
    handle = user_payload.get("handle") or ""
    if not user_id:
        die(f"auth/me 返回缺少 id/userId 字段: {info}")
    save_user_credential(host, token, int(user_id), str(handle))
    print(f"\u2713 Logged in as @{handle} (userId={user_id})")


def cmd_auth_logout(args: argparse.Namespace) -> None:
    """skillhub auth logout — 仅清空 user 字段。"""
    _ = args
    cred = load_user_credential()
    if cred is None:
        print("Already logged out")
        return
    clear_user_credential()
    print("\u2713 Logged out")


def cmd_auth_whoami(args: argparse.Namespace) -> None:
    """skillhub auth whoami — 调 GET /api/v1/auth/me 验证 token 并打印关键字段。"""
    cred = load_user_credential()
    if cred is None:
        die("未登录。请先执行: skillhub login --key skh_xxx")
    host = (getattr(args, "host", None) or "").strip() or cred.get("host") or DEFAULT_ENTERPRISE_HOST
    token = cred["token"]
    try:
        info = _get_auth_me(host, token)
    except RuntimeError as exc:
        die(f"whoami 失败: {exc}")
    if getattr(args, "json_output", False):
        print(json.dumps(info, ensure_ascii=False))
        return
    # 兼容平铺 {id,...} 与包了 user 一层 {"user":{id,...}} 两种返回结构
    user_payload = info.get("user") if isinstance(info.get("user"), dict) else info
    print(f"userId : {user_payload.get('id') or user_payload.get('userId')}")
    print(f"handle : {user_payload.get('handle')}")
    if user_payload.get("role"):
        print(f"role   : {user_payload.get('role')}")


def cmd_auth_token(args: argparse.Namespace) -> None:
    """skillhub auth token — stdout 输出当前 PAT（CI 用）。"""
    _ = args
    cred = load_user_credential()
    if cred is None:
        die("未登录")
    sys.stdout.write(cred["token"])
    sys.stdout.flush()


# ============================================================
# User PAT — publish: SKILL.md 解析 + ZIP 打包 + multipart 上传
# ============================================================


_SLUG_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
_SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


_PUBLISH_EXCLUDE_DIRS = {".git", ".idea", ".vscode", "node_modules", "__pycache__"}
_PUBLISH_EXCLUDE_PATTERNS = (".pyc", ".DS_Store", "Thumbs.db")


def _collect_skill_files(skill_dir: Path) -> List[Tuple[str, bytes]]:
    """递归收集 skill 目录下所有可发布文件，返回 [(rel_posix_path, content_bytes), ...]。

    - 路径分隔符规范化为 /（跨平台）
    - 排除 .git/.idea/.vscode/node_modules/__pycache__ 等目录
    - 排除 *.pyc / .DS_Store / Thumbs.db
    - 跳过软连接：
        * 失效软连接（断链）→ 警告并跳过，不再因 read_bytes 失败而崩溃
        * 完好软连接 → 跳过（避免打包出 skill_dir 外的内容造成安全/隐私风险）
    - 必须至少含 SKILL.md（不区分大小写）
    """
    skill_dir = skill_dir.resolve()
    if not skill_dir.is_dir():
        die(f"skill 目录不存在: {skill_dir}")
    collected: List[Tuple[str, bytes]] = []
    has_skill_md = False
    # 不跟随软连接目录（followlinks=False 是默认值，显式写出来更清晰）
    for root, dirs, files in os.walk(str(skill_dir), followlinks=False):
        dirs[:] = [d for d in dirs if d not in _PUBLISH_EXCLUDE_DIRS]
        for fname in files:
            if any(fname.endswith(suf) for suf in _PUBLISH_EXCLUDE_PATTERNS):
                continue
            abs_path = Path(root) / fname
            # 软连接处理：避免打包目录外内容 + 避免断链炸
            if abs_path.is_symlink():
                rel = abs_path.relative_to(skill_dir).as_posix()
                if not abs_path.exists():
                    print(f"warn: 跳过失效软连接 {rel}", file=sys.stderr)
                else:
                    print(f"warn: 跳过软连接 {rel}（不打包）", file=sys.stderr)
                continue
            rel = abs_path.relative_to(skill_dir).as_posix()
            try:
                data = abs_path.read_bytes()
            except OSError as exc:
                raise RuntimeError(f"读取文件失败 {abs_path}: {exc}") from exc
            collected.append((rel, data))
            if rel.lower() == "skill.md":
                has_skill_md = True
    if not has_skill_md:
        die("未找到 SKILL.md（根目录必须含 SKILL.md）")
    if not collected:
        die("skill 目录为空，无可上传文件")
    return collected


def pack_skill_zip(skill_dir: Path, dest: Path) -> None:
    """打包 skill 目录为 ZIP，跨平台兼容。

    - arcname 始终使用 / 作为路径分隔符（Windows → POSIX）
    - 每条 ZipInfo.create_system = 3（unix）；解压时不会带 Windows ACL
    - 自动排除 .git/.idea/.vscode/node_modules/__pycache__ 等目录
    - 排除 *.pyc / .DS_Store / Thumbs.db
    """
    skill_dir = skill_dir.resolve()
    if not skill_dir.is_dir():
        die(f"skill 目录不存在: {skill_dir}")
    with zipfile.ZipFile(str(dest), mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(str(skill_dir)):
            # 排除目录（in-place 修改 dirs 让 os.walk 跳过）
            dirs[:] = [d for d in dirs if d not in _PUBLISH_EXCLUDE_DIRS]
            for fname in files:
                if any(fname.endswith(suf) for suf in _PUBLISH_EXCLUDE_PATTERNS):
                    continue
                abs_path = Path(root) / fname
                rel = abs_path.relative_to(skill_dir).as_posix()  # 跨平台 → /
                # 显式构造 ZipInfo 以固定 create_system，确保 unix 解压无 ACL
                zi = zipfile.ZipInfo(filename=rel)
                zi.create_system = 3
                zi.compress_type = zipfile.ZIP_DEFLATED
                try:
                    data = abs_path.read_bytes()
                except OSError as exc:
                    raise RuntimeError(f"读取文件失败 {abs_path}: {exc}") from exc
                zf.writestr(zi, data)


def parse_skill_md_frontmatter(skill_md: Path) -> Dict[str, Any]:
    """解析 SKILL.md 头部 YAML front matter（``---`` 包裹）。

    PoC 限定：仅支持简单的 ``key: value`` 与 ``key: [a, b]`` 列表语法，避开 PyYAML 依赖。
    """
    if not skill_md.is_file():
        die(f"未找到 SKILL.md: {skill_md}")
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        die("SKILL.md 缺少 front matter（首行需为 ---）")
    parts = text.split("\n")
    if not parts or parts[0].strip() != "---":
        die("SKILL.md front matter 起始标记不正确")
    end_idx = -1
    for i in range(1, len(parts)):
        if parts[i].strip() == "---":
            end_idx = i
            break
    if end_idx < 0:
        die("SKILL.md front matter 缺少结束标记 ---")
    body = parts[1:end_idx]
    out: Dict[str, Any] = {}
    for raw in body:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if not key:
            continue
        # 简单 list: [a, b, c] 或带引号
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if not inner:
                out[key] = []
            else:
                out[key] = [_strip_yaml_scalar(s.strip()) for s in inner.split(",") if s.strip()]
        else:
            out[key] = _strip_yaml_scalar(val)
    return out


def _strip_yaml_scalar(val: str) -> str:
    """去掉首尾包裹的单/双引号。"""
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
        return val[1:-1]
    return val


def _resolve_skill_dir(path_arg: str) -> Path:
    p = Path(path_arg).expanduser().resolve()
    if not p.is_dir():
        die(f"path 必须是 skill 目录: {p}")
    return p


# 单个 zip 解压最大允许总大小（防 zip bomb）；publish 接口本身有 10MB 限制
_PUBLISH_ZIP_MAX_UNCOMPRESSED = 50 * 1024 * 1024  # 50MB


def _safe_extract_zip(zip_path: Path, dest: Path) -> None:
    """安全解压 zip 到 dest 目录。

    防御措施：
      1. zip-slip：拒绝包含 `..` / 绝对路径的成员（防穿越目标目录）
      2. zip bomb：累计解压大小超 _PUBLISH_ZIP_MAX_UNCOMPRESSED 时中断
      3. 不跟随 symlink：zipfile.extractall 默认行为符合预期
    """
    try:
        with zipfile.ZipFile(str(zip_path)) as zf:
            total_size = 0
            for info in zf.infolist():
                # 校验路径合法性
                name = info.filename
                if name.startswith("/") or name.startswith("\\"):
                    die(f"zip 包含非法绝对路径: {name}")
                if any(part == ".." for part in Path(name).parts):
                    die(f"zip 包含路径穿越: {name}")
                # 累计大小
                total_size += info.file_size
                if total_size > _PUBLISH_ZIP_MAX_UNCOMPRESSED:
                    die(
                        f"zip 解压后总大小超 {_PUBLISH_ZIP_MAX_UNCOMPRESSED // (1024 * 1024)}MB，"
                        f"疑似异常包"
                    )
            zf.extractall(str(dest))
    except zipfile.BadZipFile as exc:
        die(f"zip 文件损坏或格式错误: {zip_path} ({exc})")


def _resolve_skill_input(path_arg: str) -> Tuple[Path, Optional[Path]]:
    """解析 publish 命令的 path 参数，支持目录和 zip 文件两种形式。

    返回 (skill_dir, cleanup_dir)：
      - skill_dir：实际用于打包上传的目录
      - cleanup_dir：非 None 时表示 skill_dir 是临时解压目录，调用方应在结束后 rmtree

    支持输入：
      1. 目录（含 SKILL.md）：直接返回，cleanup_dir=None
      2. .zip 文件：解压到临时目录后返回；如果 zip 顶层只有一个目录（典型如
         `zip -r my-skill.zip my-skill/` 出来的包），自动 unwrap 那一层

    安全：zip 解压走 _safe_extract_zip，做 zip-slip + zip bomb 防护。
    """
    p = Path(path_arg).expanduser().resolve()
    if not p.exists():
        die(f"路径不存在: {p}")

    # 情况 1：目录
    if p.is_dir():
        return p, None

    # 情况 2：zip 文件
    if p.is_file() and p.suffix.lower() == ".zip":
        tmp_root = Path(tempfile.mkdtemp(prefix="skillhub-publish-"))
        try:
            _safe_extract_zip(p, tmp_root)
        except SystemExit:
            shutil.rmtree(str(tmp_root), ignore_errors=True)
            raise
        except Exception as exc:
            shutil.rmtree(str(tmp_root), ignore_errors=True)
            die(f"解压 zip 失败: {exc}")

        # 智能 unwrap：如果顶层只有一个目录，认为那个就是 skill 根
        # 忽略 . 开头的隐藏文件（如 macOS 的 __MACOSX）
        visible = [
            c for c in tmp_root.iterdir()
            if not c.name.startswith(".") and c.name != "__MACOSX"
        ]
        if len(visible) == 1 and visible[0].is_dir():
            return visible[0], tmp_root
        return tmp_root, tmp_root

    die(f"path 必须是 skill 目录或 .zip 文件: {p}")


def _load_skill_metadata(skill_dir: Path, override_version: Optional[str]) -> Dict[str, Any]:
    md = parse_skill_md_frontmatter(skill_dir / "SKILL.md")
    if override_version:
        md["version"] = override_version.strip()
    return md


def _validate_metadata(md: Dict[str, Any]) -> None:
    slug = (md.get("slug") or "").strip()
    version = (md.get("version") or "").strip()
    if not slug:
        die("SKILL.md 缺少 slug")
    if not _SLUG_PATTERN.match(slug):
        die(f"slug 不合法（必须 kebab-case 3-128 char）: {slug}")
    if len(slug) < 2 or len(slug) > 128:
        die(f"slug 长度需在 2-128 之间: {slug}")
    if not version:
        die("SKILL.md 缺少 version")
    if not _SEMVER_PATTERN.match(version):
        die(f"version 不是合法 SemVer: {version}")
    if not (md.get("displayName") or "").strip():
        die("SKILL.md 缺少 displayName")


def _post_publish_multipart(
    host: str,
    token: str,
    metadata: Dict[str, Any],
    skill_files: List[Tuple[str, bytes]],
    changelog: str,
) -> Tuple[int, Dict[str, Any]]:
    """multipart 上传：payload(JSON) + 多个 files part（每个 part 一个原始文件）。

    服务端契约（POST /api/v1/community/skills/publish）：
      - payload: JSON 字符串，含 slug/version/displayName/summary/.../changelog
      - files:   重复字段名，每个 part 的 filename 是相对路径（如 SKILL.md / docs/usage.md）
                  服务端通过 r.MultipartForm.File["files"] 取列表，
                  并从 Content-Disposition 的 filename 还原相对路径

    PoC 不引入 requests 依赖；用 urllib + 手工 multipart。
    """
    boundary = "----skillhubBoundary" + str(int(time.time() * 1000))
    payload = {
        "slug": metadata.get("slug", ""),
        "version": metadata.get("version", ""),
        "displayName": metadata.get("displayName", ""),
        "summary": metadata.get("summary", ""),
        "description": metadata.get("description", ""),
        "tags": metadata.get("tags", []) if isinstance(metadata.get("tags"), list) else [],
        "license": metadata.get("license", ""),
        "homepage": metadata.get("homepage", ""),
        "changelog": changelog,
    }
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    body = bytearray()

    def _add_part(name: str, data: bytes, *, filename: Optional[str] = None, ctype: Optional[str] = None) -> None:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        if filename:
            body.extend(
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode("utf-8")
            )
        else:
            body.extend(f'Content-Disposition: form-data; name="{name}"\r\n'.encode("utf-8"))
        body.extend(f"Content-Type: {ctype or 'application/octet-stream'}\r\n\r\n".encode("utf-8"))
        body.extend(data)
        body.extend(b"\r\n")

    _add_part("payload", payload_bytes, ctype="application/json")
    # 每个 skill 文件作为一个独立 part，name 固定为 "files"，filename 用相对路径
    for rel_path, data in skill_files:
        ctype = "text/markdown" if rel_path.lower().endswith(".md") else "application/octet-stream"
        _add_part("files", data, filename=rel_path, ctype=ctype)
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    url = host.rstrip("/") + "/api/v1/community/skills/publish"
    req = urllib.request.Request(
        url,
        data=bytes(body),
        method="POST",
        headers=cli_request_headers({
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        }),
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:  # nosec
            raw = resp.read()
            try:
                parsed = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                parsed = {"raw": raw.decode("utf-8", errors="replace")[:1024]}
            return resp.getcode(), parsed
    except urllib.error.HTTPError as exc:
        raw = b""
        try:
            raw = exc.read() or b""
        except Exception:
            pass
        try:
            parsed = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            parsed = {"raw": raw.decode("utf-8", errors="replace")[:1024]}
        return exc.code, parsed
    except urllib.error.URLError as exc:
        raise RuntimeError(f"网络错误: {exc.reason}") from exc


def _format_publish_error(status: int, body: Dict[str, Any]) -> str:
    code = str(body.get("code") or "")
    msg = str(body.get("error") or body.get("raw") or "")
    if status == 401:
        return "请先执行: skillhub login --key skh_xxx"
    if status == 403:
        return f"权限不足: {msg}"
    if status == 409:
        return f"slug 冲突: {msg}"
    if status == 429:
        # 限流命中：尽量给用户清晰的等待提示
        rule = str(body.get("rule") or "")
        retry_after = body.get("retryAfter")
        hint = f"，请 {retry_after} 秒后重试" if retry_after else ""
        if rule:
            return f"发布频率过高（命中规则 {rule}）{hint}: {msg}"
        return f"发布频率过高{hint}: {msg}"
    if 400 <= status < 500:
        return f"请求失败 ({status}): {msg} (code={code})" if code else f"请求失败 ({status}): {msg}"
    return f"服务端错误，请稍后重试 ({status}): {msg}"



# ============================================================
# skillhub verify <slug>[@<version>] —— 平台签名校验
# ============================================================
def _verify_http_get_json(url: str, timeout: int = 10) -> Tuple[int, Dict[str, Any]]:
    """简单 GET：返回 (status_code, body_json)。仅 verify 命令用。"""
    req = urllib.request.Request(url, method="GET", headers=cli_request_headers({"Accept": "application/json"}))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            data = resp.read()
            return resp.status, (json.loads(data) if data else {})
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {"error": f"HTTP {e.code}"}
        return e.code, body
    except Exception as e:
        return 0, {"error": str(e)}


def _verify_local_ed25519(public_key_b64: str, payload_str: str, signature_b64: str) -> Optional[bool]:
    """用 cryptography 库做本地 Ed25519 离线验签。
    返回 True/False/None：None 表示库不可用，调用方应降级到服务端在线验签。
    """
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError:
        return None

    try:
        pk = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64))
        pk.verify(base64.b64decode(signature_b64), payload_str.encode("utf-8"))
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False


def _resolve_api_host(args_host: str = "") -> str:
    host = (args_host or "").strip()
    if not host:
        host = os.environ.get("SKILLHUB_HOST", "").strip() or DEFAULT_ENTERPRISE_HOST
    return host.rstrip("/")


def _fetch_ranking_json(host: str, ranking_type: str, timeout: int) -> Dict[str, Any]:
    path = RANKING_ENDPOINTS.get(ranking_type)
    if not path:
        raise RuntimeError(f"Unsupported ranking type: {ranking_type}")

    api_host = _resolve_api_host(host)
    parsed = urllib.parse.urlparse(api_host)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise RuntimeError(f"Invalid API host: {api_host}")

    url = api_host.rstrip("/") + path
    req = urllib.request.Request(
        url,
        headers=cli_request_headers({
            "Accept": "application/json",
        }),
    )
    try:
        with urllib.request.urlopen(req, timeout=max(1, int(timeout))) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Failed to fetch {ranking_type} rankings: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to fetch {ranking_type} rankings: {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"Failed to fetch {ranking_type} rankings: timed out") from exc

    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from {ranking_type} rankings: {exc}") from exc
    if not isinstance(raw, dict):
        raise RuntimeError(f"Ranking response must be a JSON object: {ranking_type}")
    return raw


def cmd_rankings(args: argparse.Namespace) -> None:
    ranking_type = (getattr(args, "type", "") or "all").strip()
    host = _resolve_api_host(getattr(args, "host", "") or "")
    timeout = max(1, int(getattr(args, "timeout", 10) or 10))

    try:
        if ranking_type == "all":
            results = {
                key: _fetch_ranking_json(host, key, timeout)
                for key in RANKING_ENDPOINTS.keys()
            }
            print(json.dumps({"rankings": results}, ensure_ascii=False))
            return
        result = _fetch_ranking_json(host, ranking_type, timeout)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        die(str(exc))


def extract_available_security_reports(detail: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    raw_reports = as_dict(detail.get("securityReports"))
    reports: Dict[str, Dict[str, str]] = {}
    for source_key, output_key, provider, name in SECURITY_REPORT_SOURCES:
        if output_key in reports:
            continue
        item = as_dict(raw_reports.get(source_key))
        report_url = first_non_empty_string(item, ["reportUrl", "report_url"])
        if not report_url:
            continue
        reports[output_key] = {
            "provider": provider,
            "name": name,
            "status": str(item.get("status") or ""),
            "statusText": str(item.get("statusText") or ""),
            "reportUrl": report_url,
        }
    return reports


def cmd_skill_reports(args: argparse.Namespace) -> None:
    slug, namespace = _slug_namespace_from_args(args)

    host = _resolve_api_host(getattr(args, "host", "") or "")
    timeout = max(1, int(getattr(args, "timeout", 10) or 10))
    detail_url = append_query_params(
        f"{host}/api/v1/skills/{urllib.parse.quote(slug, safe='')}",
        {"namespace": namespace},
    )
    status, body = _verify_http_get_json(detail_url, timeout=timeout)
    if status != 200:
        die(f"无法获取 skill 详情 (HTTP {status}): {body.get('error') or body}")

    reports = extract_available_security_reports(body)
    output_slug = slug
    skill = as_dict(body.get("skill"))
    if isinstance(skill.get("slug"), str) and skill["slug"].strip():
        output_slug = skill["slug"].strip()

    if getattr(args, "json_output", False):
        print(json.dumps({"slug": output_slug, "reports": reports}, ensure_ascii=False))
        return

    for report in reports.values():
        print(report["reportUrl"])


def is_missing_skill_evaluation(status: int, body: Dict[str, Any]) -> bool:
    error = str(body.get("error") or "").strip().lower()
    return status == 404 and error == "evaluation not found"


def build_skill_evaluation_output(slug: str, evaluation: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    output: Dict[str, Any] = {"slug": slug}
    if evaluation is not None:
        output["evaluation"] = evaluation
    return output


def cmd_skill_evaluation(args: argparse.Namespace) -> None:
    slug, namespace = _slug_namespace_from_args(args)

    host = _resolve_api_host(getattr(args, "host", "") or "")
    timeout = max(1, int(getattr(args, "timeout", 10) or 10))
    evaluation_url = append_query_params(
        f"{host}/api/v1/skills/{urllib.parse.quote(slug, safe='')}/evaluation",
        {"namespace": namespace},
    )
    status, body = _verify_http_get_json(evaluation_url, timeout=timeout)
    if is_missing_skill_evaluation(status, body):
        output = build_skill_evaluation_output(slug, None)
    elif status == 200:
        output = build_skill_evaluation_output(slug, body)
    else:
        die(f"无法获取评测报告 (HTTP {status}): {body.get('error') or body}")

    if getattr(args, "json_output", False):
        print(json.dumps(output, ensure_ascii=False))
        return

    evaluation = as_dict(output.get("evaluation"))
    if not evaluation:
        return
    print(json.dumps(evaluation, ensure_ascii=False, indent=2))


def _is_mac_junk_zip_path(file_path: str) -> bool:
    if not file_path or file_path.endswith("/"):
        return True
    norm = file_path.replace("\\", "/").lstrip("./")
    if norm.startswith("__MACOSX/") or "/__MACOSX/" in norm:
        return True
    base = norm.rsplit("/", 1)[-1]
    if base == ".DS_Store":
        return True
    if base.startswith("._"):
        return True
    if base.lower() == "thumbs.db":
        return True
    return False


def _is_junk_zip_path(file_path: str) -> bool:
    norm = file_path.replace("\\", "/").lstrip("./")
    if norm == "_meta.json":
        return True
    return _is_mac_junk_zip_path(file_path)


def _compute_content_hash_from_zip(zip_path: Path, *, include_meta: bool = False) -> str:
    entries: List[Tuple[str, str]] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            rel_path = info.filename.replace("\\", "/").lstrip("./")
            if include_meta:
                if _is_mac_junk_zip_path(rel_path):
                    continue
            elif _is_junk_zip_path(rel_path):
                continue
            data = zf.read(info.filename)
            file_sha = hashlib.sha256(data).hexdigest()
            entries.append((rel_path, file_sha))
    entries.sort(key=lambda item: item[0])
    digest = hashlib.sha256()
    for rel_path, file_sha in entries:
        digest.update(f"{rel_path}:{file_sha}\n".encode("utf-8"))
    return digest.hexdigest()


def _compute_content_hash_from_dir(skill_dir: Path, *, include_meta: bool = False) -> str:
    entries: List[Tuple[str, str]] = []
    root = skill_dir.resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_path = path.relative_to(root).as_posix()
        if include_meta:
            if _is_mac_junk_zip_path(rel_path):
                continue
        elif _is_junk_zip_path(rel_path):
            continue
        file_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append((rel_path, file_sha))
    entries.sort(key=lambda item: item[0])
    digest = hashlib.sha256()
    for rel_path, file_sha in entries:
        digest.update(f"{rel_path}:{file_sha}\n".encode("utf-8"))
    return digest.hexdigest()


def _match_local_to_signed_content_hash(
    local_path: Path,
    expected_hash: str,
    *,
    from_zip: bool,
) -> Tuple[bool, str, str]:
    """比对本地 zip 或已安装目录的指纹与签名 payload 中的 content_hash。

    存量签名可能含 _meta.json（backfill/sync），新发布通常不含；两种都算，能对上即可。
    返回 (matched, actual_hash_for_display, hash_mode)。
    """
    expected = expected_hash.strip().lower()
    fallback_actual = ""
    compute = _compute_content_hash_from_zip if from_zip else _compute_content_hash_from_dir
    for mode, include_meta in (("content", False), ("content+meta", True)):
        actual = compute(local_path, include_meta=include_meta).lower()
        if not fallback_actual:
            fallback_actual = actual
        if actual == expected:
            return True, actual, mode
    return False, fallback_actual, "content"


def _match_zip_to_signed_content_hash(
    zip_path: Path, expected_hash: str
) -> Tuple[bool, str, str]:
    return _match_local_to_signed_content_hash(zip_path, expected_hash, from_zip=True)


def _resolve_skill_version_from_api(host: str, slug: str, version: str, namespace: str = "") -> str:
    if version:
        return version
    detail_url = append_query_params(
        f"{host}/api/v1/skills/{urllib.parse.quote(slug, safe='')}",
        {"namespace": namespace},
    )
    st, body = _verify_http_get_json(detail_url)
    if st != 200:
        die(f"无法获取 skill 详情 (HTTP {st}): {body.get('error') or body}")
    resolved = ((body.get("latestVersion") or {}).get("version") or "").strip()
    if not resolved:
        die("详情接口未返回 latestVersion，请显式指定 <slug>@<version>")
    return resolved


def _fetch_signature(host: str, slug: str, version: str, namespace: str = "") -> Dict[str, Any]:
    signature_url = append_query_params(
        f"{host}/api/v1/open/skills/{urllib.parse.quote(slug, safe='')}/versions/{urllib.parse.quote(version, safe='')}/signature",
        {"namespace": namespace},
    )
    st, sig = _verify_http_get_json(
        signature_url
    )
    if st == 404:
        die(f"找不到该版本: {slug}@{version}", code=2)
    if st != 200:
        die(f"拉取签名失败 (HTTP {st}): {sig.get('error') or sig}")
    return sig


def _verify_signature_record(
    host: str,
    slug: str,
    version: str,
    sig: Dict[str, Any],
    namespace: str = "",
) -> Tuple[bool, str, Dict[str, Any]]:
    if not sig.get("signed"):
        return False, "not_signed", {
            "ok": False,
            "reason": "not_signed",
            "content_hash": sig.get("content_hash"),
        }

    payload_str = sig.get("payload") or ""
    signature_b64 = sig.get("signature") or ""
    key_id = sig.get("key_id") or ""
    if not (payload_str and signature_b64 and key_id):
        die("签名响应不完整，缺少 payload/signature/key_id")

    st, keys_resp = _verify_http_get_json(f"{host}/api/v1/open/platform/keys")
    if st != 200:
        die(f"拉取公钥列表失败 (HTTP {st}): {keys_resp.get('error') or keys_resp}")
    pk_b64 = ""
    for key in keys_resp.get("keys", []):
        if key.get("key_id") == key_id:
            pk_b64 = key.get("public_key_raw_b64") or ""
            break
    if not pk_b64:
        die(f"未找到对应公钥 (key_id={key_id})，密钥可能已撤销", code=2)

    local = _verify_local_ed25519(pk_b64, payload_str, signature_b64)
    if local is True:
        ok, verify_mode = True, "local"
    elif local is False:
        ok, verify_mode = False, "local"
    else:
        verify_url = append_query_params(
            f"{host}/api/v1/open/skills/{urllib.parse.quote(slug, safe='')}/versions/{urllib.parse.quote(version, safe='')}/verify-signature",
            {"namespace": namespace},
        )
        st, vr = _verify_http_get_json(verify_url)
        if st != 200:
            die(f"服务端验签失败 (HTTP {st}): {vr.get('error') or vr}")
        ok, verify_mode = bool(vr.get("verified")), "remote"

    payload_obj: Dict[str, Any] = {}
    try:
        payload_obj = json.loads(payload_str)
    except Exception:
        payload_obj = {}

    result = {
        "ok": ok,
        "slug": slug,
        "version": version,
        "key_id": key_id,
        "verify_mode": verify_mode,
        "issuer": payload_obj.get("issuer"),
        "publisher_user_name": payload_obj.get("publisher_user_name"),
        "publisher_real_name_verified": payload_obj.get("publisher_real_name_verified"),
        "issued_at": payload_obj.get("issued_at"),
        "content_hash": payload_obj.get("content_hash") or sig.get("content_hash"),
    }
    return ok, verify_mode, result


def _verify_local_against_signature(
    local_path: Path,
    host: str,
    slug: str,
    version: str,
    *,
    from_zip: bool,
    namespace: str = "",
) -> Dict[str, Any]:
    sig = _fetch_signature(host, slug, version, namespace)
    ok, verify_mode, result = _verify_signature_record(host, slug, version, sig, namespace)
    local_key = "zip_path" if from_zip else "local_path"
    if not ok:
        result[local_key] = str(local_path)
        return result

    expected_hash = str(result.get("content_hash") or "").strip().lower()
    if not expected_hash:
        die("签名记录缺少 content_hash，无法验内容")

    content_ok, actual_hash, hash_mode = _match_local_to_signed_content_hash(
        local_path, expected_hash, from_zip=from_zip
    )
    result["content_hash_match"] = content_ok
    result["content_hash_mode"] = hash_mode
    result["actual_content_hash"] = actual_hash
    result[local_key] = str(local_path)
    result["local_kind"] = "zip" if from_zip else "installed"
    result["ok"] = ok and content_ok
    if not content_ok:
        result["verify_mode"] = f"{verify_mode}+content_mismatch"
    return result


def _verify_zip_against_signature(
    zip_path: Path, host: str, slug: str, version: str, namespace: str = ""
) -> Dict[str, Any]:
    return _verify_local_against_signature(
        zip_path, host, slug, version, from_zip=True, namespace=namespace
    )


def _verify_installed_against_signature(
    skill_dir: Path, host: str, slug: str, version: str, namespace: str = ""
) -> Dict[str, Any]:
    return _verify_local_against_signature(
        skill_dir, host, slug, version, from_zip=False, namespace=namespace
    )


def _installed_skill_keys(slug: str, namespace: str = "") -> List[str]:
    keys: List[str] = []
    namespaced = display_skill_coordinate(slug, namespace)
    for key in (namespaced, slug):
        key = str(key or "").strip()
        if key and key not in keys:
            keys.append(key)
    return keys


def _resolve_installed_skill_dir(install_root: Path, slug: str, namespace: str = "") -> Optional[Path]:
    for key in _installed_skill_keys(slug, namespace):
        target = (install_root / key).expanduser().resolve()
        if target.is_dir():
            return target
    return None


def _version_from_lockfile(install_root: Path, slug: str, namespace: str = "") -> str:
    lock = load_lockfile(install_root)
    skills = lock.get("skills", {})
    if not isinstance(skills, dict):
        return ""
    for key in _installed_skill_keys(slug, namespace):
        meta = skills.get(key)
        if isinstance(meta, dict):
            return str(meta.get("version", "")).strip()
    return ""


def _print_verify_result(result: Dict[str, Any], *, slug: str, version: str) -> int:
    local_kind = result.get("local_kind")
    if result.get("ok"):
        label = "已安装目录" if local_kind == "installed" else "zip"
        print(f"✅ 签名与内容校验通过 ({result.get('verify_mode')})")
        print(f"   {slug}@{version}（{label}）")
        print(f"   内容指纹: {result.get('content_hash')}")
        return 0
    if result.get("reason") == "not_signed":
        print(f"⚠ 该版本尚未签名 (content_hash={(result.get('content_hash') or '')[:24]}…)")
        return 2
    if result.get("content_hash_match") is False:
        label = "已安装目录" if local_kind == "installed" else "zip"
        print(f"❌ 内容指纹不匹配，{label} 可能被篡改或版本不对")
        print(f"   expected: {result.get('content_hash')}")
        print(f"   actual:   {result.get('actual_content_hash')}")
        return 2
    print(f"❌ 签名验证失败 ({result.get('verify_mode')})")
    return 2


def cmd_verify(args: argparse.Namespace) -> None:
    """
    skillhub verify <slug>[@<version>] [--host URL] [--zip PATH] [--json]

    验本机 skill 内容与平台签名是否一致。默认检查 install 目录下已安装副本；
    也可用 --zip 指定下载的 zip。不单独提供「只验平台签名、不验本机文件」模式。
    """
    spec = (args.target or "").strip()
    if not spec:
        die("用法: skillhub verify <slug>[@<version>]")
    try:
        parsed_namespace, slug, parsed_version = parse_skill_ref(spec)
    except ValueError as exc:
        die(str(exc))
    namespace_arg = normalize_namespace_arg(getattr(args, "namespace", ""))
    parsed_namespace = normalize_namespace_arg(parsed_namespace)
    if namespace_arg and parsed_namespace and namespace_arg != parsed_namespace:
        die("请不要同时使用 @namespace/slug 和 --namespace，或确保两者一致")
    namespace = namespace_arg or parsed_namespace
    version = str(getattr(args, "version", "") or parsed_version or "").strip()
    if not slug:
        die("缺少 slug")
    json_mode = bool(getattr(args, "json_output", False))
    host = _resolve_api_host(getattr(args, "host", "") or "")
    install_root = Path(args.dir).expanduser().resolve()

    zip_path_str = (getattr(args, "zip_path", "") or "").strip()
    if zip_path_str:
        local_path = Path(zip_path_str).expanduser().resolve()
        if not local_path.is_file():
            die(f"zip 文件不存在: {local_path}")
        from_zip = True
    else:
        local_path = _resolve_installed_skill_dir(install_root, slug, namespace)
        if local_path is None:
            expected_paths = ", ".join(str(install_root / key) for key in _installed_skill_keys(slug, namespace))
            die(
                f"未找到已安装的 skill 目录: {expected_paths}\n"
                f"  请先 skillhub install {display_skill_coordinate(slug, namespace)}，或用 --zip 指定 zip 路径"
            )
        from_zip = False
        if not version:
            version = _version_from_lockfile(install_root, slug, namespace)

    version = _resolve_skill_version_from_api(host, slug, version, namespace)
    verify_fn = _verify_zip_against_signature if from_zip else _verify_installed_against_signature
    result = verify_fn(local_path, host, slug, version, namespace)

    if json_mode:
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0 if result.get("ok") else 2)

    sys.exit(_print_verify_result(result, slug=slug, version=version))


def cmd_publish(args: argparse.Namespace) -> None:
    """skillhub publish ./skill-dir 或 ./skill.zip [--version 1.2.0] [--changelog ...] [--dry-run] [--token ...] [--json]"""
    skill_dir, cleanup_dir = _resolve_skill_input(args.path)
    try:
        metadata = _load_skill_metadata(skill_dir, override_version=getattr(args, "version", None))
        _validate_metadata(metadata)

        json_out = bool(getattr(args, "json_output", False))

        if getattr(args, "dry_run", False):
            if json_out:
                print(json.dumps({"dryRun": True, "slug": metadata["slug"], "version": metadata["version"]}))
            else:
                print(f"\u2713 Dry-run passed: {metadata['slug']}@{metadata['version']}")
            return

        token, host = resolve_user_token(args)

        try:
            skill_files = _collect_skill_files(skill_dir)
        except RuntimeError as exc:
            die(f"收集 skill 文件失败: {exc}")

        try:
            status, body = _post_publish_multipart(
                host=host,
                token=token,
                metadata=metadata,
                skill_files=skill_files,
                changelog=str(getattr(args, "changelog", "") or ""),
            )
        except RuntimeError as exc:
            die(str(exc))

        if 200 <= status < 300:
            if json_out:
                print(json.dumps(body, ensure_ascii=False))
            else:
                skill_id = body.get("skillId")
                published_status = body.get("status")
                public_url = body.get("publicUrl")
                print(f"\u2713 Published: skillId={skill_id} status={published_status}")
                if public_url:
                    print(f"  url: {public_url}")
            return

        err_msg = _format_publish_error(status, body)
        if json_out:
            print(json.dumps({"success": False, "status": status, "error": err_msg, "body": body}, ensure_ascii=False))
            raise SystemExit(1)
        die(err_msg)
    finally:
        # zip 模式时清理临时解压目录
        if cleanup_dir is not None:
            shutil.rmtree(str(cleanup_dir), ignore_errors=True)




def cmd_login(args: argparse.Namespace) -> None:
    """登录 SkillHub: skh_ key 走个人社区版，其余 key 走企业源。"""
    api_key = args.key.strip()
    if not api_key:
        die("--key is required")

    if api_key.startswith("skh_"):
        cmd_auth_login(argparse.Namespace(token=api_key, host=args.host))
        return

    host = (args.host or "").strip() or DEFAULT_ENTERPRISE_HOST

    # 调用 verify 接口
    try:
        org_info = verify_api_key(host, api_key)
    except RuntimeError as exc:
        die(f"Login failed: {exc}")

    org_id = org_info["orgId"]
    org_org_id = org_info.get("orgOrgId", org_info["orgSlug"])  # 团队 ID（不可变）
    org_slug = org_info["orgSlug"]  # 英文简称（可变）
    org_name = org_info.get("orgName", org_org_id)

    # 加载现有凭证
    creds = load_credentials()
    orgs = creds.setdefault("orgs", {})

    # 迁移旧格式：如果存在以 orgSlug 为 key 的旧凭证，删除它
    if org_slug != org_org_id and org_slug in orgs:
        del orgs[org_slug]
        print(f"Migrating credentials from @{org_slug} to @{org_org_id}", file=sys.stderr)

    # 检查是否已存在（覆盖）
    if org_org_id in orgs:
        print(f"Updating credentials for @{org_org_id}", file=sys.stderr)

    # 写入凭证，key 为团队 ID（不可变）
    orgs[org_org_id] = {
        "orgId": org_id,
        "orgOrgId": org_org_id,
        "orgSlug": org_slug,
        "orgName": org_name,
        "host": host,
        "apiKey": api_key,
        "loggedInAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    creds["version"] = 1

    # 检查是否首次 login（打印安全警告）
    is_first_login = len(orgs) == 1 and org_org_id in orgs
    save_credentials(creds)

    if is_first_login:
        cred_path = get_credentials_path()
        print(
            f"WARNING! Your API key is stored unencrypted in '{cred_path}'.\n"
            f"Configure a credential helper to remove this warning.",
            file=sys.stderr,
        )

    print(f"\u2713 Logged in to {org_name} (@{org_org_id}) at {host}")


def cmd_logout(args: argparse.Namespace) -> None:
    """登出企业源: skillhub logout [--org <orgSlug|orgOrgId>]"""
    creds = load_credentials()
    orgs = creds.get("orgs", {})

    org_input = (args.org or "").strip().lstrip("@")

    if not org_input:
        # 如果只有一个 org，直接登出
        if len(orgs) == 1:
            org_input = next(iter(orgs))
        elif len(orgs) == 0:
            die("No enterprise sources configured. Nothing to logout.")
        else:
            org_list = ", ".join(f"@{s}" for s in orgs.keys())
            die(f"Multiple enterprise sources configured ({org_list}). Please specify --org <orgSlug>.")

    # 精确匹配 key（团队 ID）
    matched_key = None
    if org_input in orgs:
        matched_key = org_input
    else:
        # Fallback: 按 orgOrgId 或 orgSlug 字段遍历匹配
        for key, info in orgs.items():
            if info.get("orgOrgId") == org_input or info.get("orgSlug") == org_input:
                matched_key = key
                break

    if not matched_key:
        die(f"Not logged in to @{org_input}.")

    del orgs[matched_key]
    save_credentials(creds)
    print(f"\u2713 Logged out from @{matched_key}")


def cmd_config_list(args: argparse.Namespace) -> None:
    """查看已配置的企业源: skillhub config list"""
    orgs = get_all_org_credentials()

    if not orgs:
        print("No enterprise sources configured.")
        print('Run "skillhub login --key <api-key>" to add one.')
        return

    print("Enterprise Sources:")
    for key, info in orgs.items():
        host = info.get("host", DEFAULT_ENTERPRISE_HOST)
        org_id = info.get("orgId", "?")
        org_org_id = info.get("orgOrgId", key)
        org_slug = info.get("orgSlug", key)
        org_name = info.get("orgName", "")
        api_key = mask_api_key(info.get("apiKey", ""))
        logged_in = info.get("loggedInAt", "?")
        print(f"  @{key}")
        if org_name:
            print(f"    Name:      {org_name}")
        print(f"    Org ID:    {org_id}")
        print(f"    Team ID:   {org_org_id}")
        if org_slug != org_org_id:
            print(f"    Slug:      {org_slug}")
        print(f"    Host:      {host}")
        print(f"    API Key:   {api_key}")
        print(f"    Logged in: {logged_in}")
        print()


def _try_resolve_community_namespace(
    namespace: str, slug: str, version: Optional[str], *, json_out: bool = False
) -> Optional[Dict[str, Any]]:
    """尝试通过 resolve API 解析 @namespace/slug 社区坐标。

    返回 skill 详情 dict（成功）或 None（不是社区 namespace，fallback 企业源）。
    """
    host = os.environ.get("SKILLHUB_HOST", "").strip() or DEFAULT_ENTERPRISE_HOST
    coordinate = f"@{namespace}/{slug}"
    url = f"{host}/api/v1/skills/resolve?coordinate={urllib.parse.quote(coordinate, safe='@/')}"
    req = urllib.request.Request(url, headers=cli_request_headers({"Accept": "application/json"}))
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status and resp.status >= 400:
                return None
            body = json.loads(resp.read().decode("utf-8"))
            if not isinstance(body, dict):
                return None
            return body
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None  # 不是社区 namespace，fallback 企业源
        if not json_out:
            print(f"warn: resolve @namespace/slug failed (HTTP {exc.code}), fallback to enterprise source", file=sys.stderr)
        return None
    except Exception:
        return None


def _install_community_resolved_skill(
    args: argparse.Namespace,
    resolved: Dict[str, Any],
    original_slug: str,
    version: Optional[str],
    *,
    json_out: bool = False,
) -> None:
    """安装通过 resolve API 解析的社区 namespace skill。

    resolved 是 resolve API 返回的 skill 详情 dict（包含 slug 用于下载）。
    """
    # resolve 返回详情结构：skill.slug 是内部下载 slug，namespace.canonicalName 是公开坐标。
    skill_info = resolved.get("skill") if isinstance(resolved.get("skill"), dict) else {}
    internal_slug = str(skill_info.get("slug") or resolved.get("slug") or original_slug).strip()
    ns_info = resolved.get("namespace")
    ns_dict = ns_info if isinstance(ns_info, dict) else {}
    namespace_handle = normalize_namespace_arg(ns_dict.get("handle") or getattr(args, "namespace", ""))
    public_slug = str(ns_dict.get("publicSlug") or original_slug).strip()
    canonical_name = str(ns_dict.get("canonicalName") or display_skill_coordinate(public_slug, namespace_handle)).strip()
    display_name = str(skill_info.get("displayName") or resolved.get("displayName") or internal_slug)
    latest = resolved.get("latestVersion") if isinstance(resolved.get("latestVersion"), dict) else {}
    resolved_version = str(latest.get("version") or skill_info.get("version") or "").strip()

    if not json_out:
        ns_display = ""
        if canonical_name:
            ns_display = f" ({canonical_name})"
        print(f"info: resolved community skill{ns_display}, internal slug={internal_slug}", file=sys.stderr)

    original_slug_attr = args.slug
    args.slug = internal_slug
    try:
        skill = {
            "slug": internal_slug,
            "name": display_name,
            "version": resolved_version,
            "source": skill_info.get("source") or "community",
        }

        install_root = Path(getattr(args, "dir", DEFAULT_INSTALL_ROOT)).expanduser().resolve()
        install_key = canonical_name or internal_slug
        target_dir = install_root / install_key
        expected_sha256 = str(skill.get("sha256", "")).strip().lower()

        # 优先用 API 下载（支持 namespace 的 package_cos_key）
        host = os.environ.get("SKILLHUB_HOST", "").strip() or DEFAULT_ENTERPRISE_HOST
        api_download_url = append_query_params(
            f"{host}/api/v1/download",
            {
                "slug": public_slug or internal_slug,
                "namespace": namespace_handle,
                "version": version or "",
            },
        )

        install_zip_to_target_with_fallback(
            slug=internal_slug,
            zip_uris=[api_download_url],
            target_dir=target_dir,
            force=getattr(args, "force", False),
            expected_sha256=expected_sha256,
        )

        lock = load_lockfile(install_root)
        skills_lock = lock.setdefault("skills", {})
        skills_lock[install_key] = {
            "name": skill.get("name", display_name),
            "zip_url": api_download_url,
            "source": normalize_source_label(skill.get("source")),
            "version": str(skill.get("version", "")).strip(),
            "namespace": ns_info,
            "internalSlug": internal_slug,
            "publicSlug": public_slug,
            "installDir": str(target_dir),
        }
        save_lockfile(install_root, lock)

        if json_out:
            print(json.dumps({
                "success": True,
                "slug": install_key,
                "publicSlug": public_slug,
                "internalSlug": internal_slug,
                "namespace": ns_info,
                "version": str(skill.get("version", "")).strip(),
                "targetDir": str(target_dir),
            }, ensure_ascii=False))
        else:
            print(f"\u2713 Installed: {install_key} -> {target_dir}")
    finally:
        args.slug = original_slug_attr


def cmd_install(args: argparse.Namespace) -> None:
    json_out = bool(getattr(args, "json_output", False))
    raw_slug = args.slug.strip()
    namespace_arg = normalize_namespace_arg(getattr(args, "namespace", ""))

    # 解析 @org/slug@version 格式
    try:
        org, slug, version = parse_skill_ref(raw_slug)
    except ValueError as exc:
        if json_out:
            print(json.dumps({"success": False, "slug": raw_slug, "error": str(exc)}))
            raise SystemExit(1)
        die(str(exc))

    if namespace_arg and org and namespace_arg != org:
        message = "请不要同时使用 @namespace/slug 和 --namespace，或确保两者一致"
        if json_out:
            print(json.dumps({"success": False, "slug": raw_slug, "error": message}, ensure_ascii=False))
            raise SystemExit(1)
        die(message)
    if namespace_arg and not org:
        resolved = _try_resolve_community_namespace(namespace_arg, slug, version, json_out=json_out)
        if resolved is None:
            message = f"community skill not found: {slug} --namespace {namespace_arg}"
            if json_out:
                print(json.dumps({"success": False, "slug": slug, "namespace": namespace_arg, "error": message}, ensure_ascii=False))
                raise SystemExit(1)
            die(message)
        _install_community_resolved_skill(args, resolved, slug, version, json_out=json_out)
        return

    # 企业源安装路径
    if org:
        # 先尝试社区 namespace 解析：@namespace/slug 可能是社区命名空间而非企业源
        # resolve API 返回 200 → 走社区下载；404 → fallback 企业源
        resolved = _try_resolve_community_namespace(org, slug, version, json_out=json_out)
        if resolved is not None:
            _install_community_resolved_skill(args, resolved, slug, version, json_out=json_out)
            return
        _install_enterprise_skill(args, org, slug, version, json_out=json_out)
        return

    # 社区源安装路径（原有逻辑，向后兼容）
    data: Dict[str, Any] = {"skills": []}
    try:
        data = load_index(args.index)
    except SystemExit:
        if not json_out:
            print(f"warn: failed to load index ({args.index}), continue with remote/direct install", file=sys.stderr)
    skill = find_skill(data, slug)
    if not skill:
        remote = fetch_remote_search_results(
            search_url=args.search_url,
            query=slug,
            limit=args.search_limit,
            timeout=args.search_timeout,
        )
        if remote:
            exact = next((x for x in remote if str(x.get("slug", "")).strip() == slug), None)
            if exact:
                skill = exact
                if not json_out:
                    print(f'info: "{slug}" not in index, using remote registry exact match', file=sys.stderr)
            else:
                if not json_out:
                    print(
                        f'info: "{slug}" not in index, and remote search has no exact slug match; '
                        "try direct download by slug",
                        file=sys.stderr,
                    )

    if not skill:
        skill = {"slug": slug, "name": slug, "version": "", "source": "skillhub"}
        if not json_out:
            print(f'info: "{slug}" not in index/remote search, try direct download by slug', file=sys.stderr)

    primary_zip_url = fill_slug_template(args.primary_download_url_template, slug)
    if not primary_zip_url:
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": "Primary download URL template resolved empty URL"}))
            raise SystemExit(1)
        die("Primary download URL template resolved empty URL")

    install_root = Path(args.dir).expanduser().resolve()
    target_dir = install_root / slug
    expected_sha256 = str(skill.get("sha256", "")).strip().lower()

    # 同名冲突检测：如果已安装的是企业版技能，自动覆盖并提示
    lock = load_lockfile(install_root)
    skills_lock = lock.setdefault("skills", {})
    existing = skills_lock.get(slug)
    force = args.force
    if existing and existing.get("source", "").startswith("@"):
        old_source = existing.get("source", "unknown")
        old_version = existing.get("version", "?")
        if not json_out:
            print(
                f"\u26a0\ufe0f  Replacing existing skill \"{slug}\" ({old_source} v{old_version}) "
                f"with community {slug}",
                file=sys.stderr,
            )
        force = True

    try:
        if json_out:
            _saved_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")
        install_zip_to_target_with_fallback(
            slug=slug,
            zip_uris=[primary_zip_url],
            target_dir=target_dir,
            force=force,
            expected_sha256=expected_sha256,
            quiet=json_out,
        )
    except SystemExit as exc:
        if json_out:
            sys.stderr.close()
            sys.stderr = _saved_stderr
            err_detail = getattr(exc, "die_message", f"Install failed for {slug}")
            print(json.dumps({"success": False, "slug": slug, "error": err_detail}))
        raise
    finally:
        if json_out and sys.stderr is not _saved_stderr:  # type: ignore[possibly-undefined]
            sys.stderr.close()
            sys.stderr = _saved_stderr  # type: ignore[possibly-undefined]

    installed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    skill_version = str(skill.get("version", "")).strip()
    skills_lock[slug] = {
        "name": skill.get("name", slug),
        "zip_url": primary_zip_url,
        "source": "community",
        "version": skill_version,
        "installedAt": installed_at,
    }
    save_lockfile(install_root, lock)
    update_clawhub_lock_v1(slug, skill_version)
    if json_out:
        print(json.dumps({
            "success": True,
            "slug": slug,
            "name": skill.get("name", slug),
            "version": skill_version,
            "source": "community",
            "org": "",
            "installedAt": installed_at,
            "targetDir": str(target_dir),
        }))
    else:
        print(f"\u2713 Installed: {slug} -> {target_dir}")


# ─── install-soul ────────────────────────────────────────────────────────────────


def cmd_install_soul(args: argparse.Namespace) -> None:
    """Install a Soul independently by slug."""
    json_out = bool(getattr(args, "json_output", False))
    slug = args.slug.strip()
    if not slug:
        if json_out:
            print(json.dumps({"success": False, "error": "slug is required"}))
            raise SystemExit(1)
        die("slug is required")

    host = os.environ.get("SKILLHUB_HOST", "").strip() or DEFAULT_ENTERPRISE_HOST
    url = f"{host}/api/v1/souls/{urllib.parse.quote(slug, safe='')}/download"

    install_root = Path(getattr(args, "dir", DEFAULT_INSTALL_ROOT)).expanduser().resolve()
    force = getattr(args, "force", False)

    # Determine output path for SOUL.md
    # Default: project root (parent of install_root / skills dir)
    output_dir = getattr(args, "output", "").strip()
    if output_dir:
        soul_path = Path(output_dir).expanduser().resolve() / "SOUL.md"
    else:
        soul_path = install_root.parent / "SOUL.md"

    if soul_path.exists() and not force:
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": f"SOUL.md already exists at {soul_path}. Use --force to overwrite."}))
            raise SystemExit(1)
        die(f"SOUL.md already exists at {soul_path}. Use --force to overwrite.")

    # Download soul content from backend
    if not json_out:
        print(f"Downloading soul: {slug}", file=sys.stderr)

    req = urllib.request.Request(url, headers=cli_request_headers({"Accept": "text/markdown,*/*"}))
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status and response.status >= 400:
                raise RuntimeError(f"Download failed ({response.status}) for soul '{slug}'")
            content = response.read().decode("utf-8")
            soul_version = response.headers.get("X-Soul-Version", "")
            content_sha256 = response.headers.get("X-Content-SHA256", "")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            err_msg = f"Soul '{slug}' not found"
        else:
            err_msg = f"Download failed (HTTP {exc.code}) for soul '{slug}'"
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": err_msg}))
            raise SystemExit(1)
        die(err_msg)
    except Exception as exc:
        err_msg = f"Failed to download soul '{slug}': {exc}"
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": err_msg}))
            raise SystemExit(1)
        die(err_msg)

    if not content.strip():
        err_msg = f"Soul '{slug}' has empty content"
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": err_msg}))
            raise SystemExit(1)
        die(err_msg)

    # Write SOUL.md
    soul_path.parent.mkdir(parents=True, exist_ok=True)
    soul_path.write_text(content, encoding="utf-8")

    # Update lockfile with soul info
    lock = load_lockfile(install_root)
    installed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    lock["soul"] = {
        "slug": slug,
        "version": soul_version,
        "sha256": content_sha256,
        "path": str(soul_path),
        "installedAt": installed_at,
    }
    save_lockfile(install_root, lock)

    if json_out:
        print(json.dumps({
            "success": True,
            "slug": slug,
            "version": soul_version,
            "path": str(soul_path),
            "installedAt": installed_at,
        }))
    else:
        print(f"\u2713 Soul '{slug}' installed to {soul_path}")


# ─── install-pack ────────────────────────────────────────────────────────────────


def cmd_install_pack(args: argparse.Namespace) -> None:
    """Install a skill pack (SkillSet) independently by slug."""
    json_out = bool(getattr(args, "json_output", False))
    slug = args.slug.strip()
    if not slug:
        if json_out:
            print(json.dumps({"success": False, "error": "slug is required"}))
            raise SystemExit(1)
        die("slug is required")

    host = os.environ.get("SKILLHUB_HOST", "").strip() or DEFAULT_ENTERPRISE_HOST
    url = f"{host}/api/v1/skillsets/{urllib.parse.quote(slug, safe='')}/download"

    install_root = Path(getattr(args, "dir", DEFAULT_INSTALL_ROOT)).expanduser().resolve()
    force = getattr(args, "force", False)

    # Download skillset zip from backend
    if not json_out:
        print(f"Downloading skill pack: {slug}", file=sys.stderr)

    req = urllib.request.Request(url, headers=cli_request_headers({"Accept": "application/zip,*/*"}))
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status and response.status >= 400:
                raise RuntimeError(f"Download failed ({response.status}) for skill pack '{slug}'")
            zip_bytes = response.read()
            pack_version = response.headers.get("X-SkillSet-Version", "")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            err_msg = f"Skill pack '{slug}' not found"
        else:
            err_msg = f"Download failed (HTTP {exc.code}) for skill pack '{slug}'"
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": err_msg}))
            raise SystemExit(1)
        die(err_msg)
    except Exception as exc:
        err_msg = f"Failed to download skill pack '{slug}': {exc}"
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": err_msg}))
            raise SystemExit(1)
        die(err_msg)

    # Parse zip: extract manifest.json and skillset prompt files.
    # Supports two package formats:
    #   1. Single skillset: manifest.json + identify.md
    #   2. Soul combination: manifest.json + soul.md + skillsets/*.md
    try:
        import io
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            # Validate zip entries for safety
            for member in zf.infolist():
                member_path = Path(member.filename)
                if member_path.is_absolute() or ".." in member_path.parts:
                    raise RuntimeError(f"Unsafe zip path entry: {member.filename}")

            manifest_raw = zf.read("manifest.json")
            manifest = json.loads(manifest_raw.decode("utf-8"))

            # Detect package format and extract skillset prompts.
            # skillset_prompts: dict mapping skillset-slug -> prompt content
            skillset_prompts: Dict[str, str] = {}
            soul_md = ""
            zip_names = zf.namelist()

            # Format 2: Soul combination package (skillsets/*.md + soul.md)
            skillset_files = [n for n in zip_names if n.startswith("skillsets/") and n.endswith(".md")]
            if skillset_files:
                for sf in skillset_files:
                    # "skillsets/tech-code-review.md" -> "tech-code-review"
                    ss_slug = sf.removeprefix("skillsets/").removesuffix(".md")
                    if ss_slug:
                        skillset_prompts[ss_slug] = zf.read(sf).decode("utf-8")
                if "soul.md" in zip_names:
                    soul_md = zf.read("soul.md").decode("utf-8")

            # Format 1: Single skillset package (identify.md)
            elif "identify.md" in zip_names:
                skillset_prompts[slug] = zf.read("identify.md").decode("utf-8")

    except KeyError:
        err_msg = f"Skill pack zip for '{slug}' is missing manifest.json"
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": err_msg}))
            raise SystemExit(1)
        die(err_msg)
    except Exception as exc:
        err_msg = f"Failed to parse skill pack zip for '{slug}': {exc}"
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": err_msg}))
            raise SystemExit(1)
        die(err_msg)

    # Collect all skill slugs from manifest.
    # Format 2 (Soul combination) has skillSets[].skillSlugs, Format 1 has top-level skillSlugs.
    manifest_skillsets = manifest.get("skillSets", [])
    all_skill_slugs: List[str] = []
    skillset_skill_map: Dict[str, List[str]] = {}  # skillset-slug -> [skill-slugs]

    if manifest_skillsets and isinstance(manifest_skillsets, list):
        # Format 2: Soul combination package
        for ss in manifest_skillsets:
            ss_slug = ss.get("slug", "")
            ss_skills = ss.get("skillSlugs", [])
            if ss_slug and isinstance(ss_skills, list):
                skillset_skill_map[ss_slug] = [s.strip() for s in ss_skills if s.strip()]
                all_skill_slugs.extend(skillset_skill_map[ss_slug])
    else:
        # Format 1: Single skillset package
        top_skills = manifest.get("skillSlugs", [])
        if isinstance(top_skills, list):
            all_skill_slugs = [s.strip() for s in top_skills if s.strip()]
            skillset_skill_map[slug] = all_skill_slugs

    # Deduplicate while preserving order
    seen: set = set()
    unique_skill_slugs: List[str] = []
    for s in all_skill_slugs:
        if s not in seen:
            seen.add(s)
            unique_skill_slugs.append(s)
    all_skill_slugs = unique_skill_slugs

    if not json_out:
        if manifest_skillsets:
            print(f"Package contains {len(skillset_skill_map)} skillset(s), {len(all_skill_slugs)} skill(s) total", file=sys.stderr)
            for ss_slug, ss_skills in skillset_skill_map.items():
                print(f"  SkillSet '{ss_slug}': {', '.join(ss_skills)}", file=sys.stderr)
        else:
            print(f"Skill pack '{slug}' contains {len(all_skill_slugs)} skill(s): {', '.join(all_skill_slugs)}", file=sys.stderr)

    # Install each skill using the existing install mechanism
    primary_url_template = (
        os.environ.get("SKILLHUB_PRIMARY_DOWNLOAD_URL_TEMPLATE", "").strip()
        or CLI_METADATA.get("skills_primary_download_url_template", "")
        or DEFAULT_PRIMARY_DOWNLOAD_URL_TEMPLATE_FALLBACK
    )
    installed_skills: List[str] = []
    failed_skills: List[Dict[str, str]] = []

    for skill_slug in all_skill_slugs:
        target_dir = install_root / skill_slug
        if target_dir.exists() and not force:
            if not json_out:
                print(f"  \u229c {skill_slug} (already installed, skip)", file=sys.stderr)
            installed_skills.append(skill_slug)
            continue
        primary_zip_url = primary_url_template.replace("{slug}", skill_slug)
        try:
            install_zip_to_target_with_fallback(
                slug=skill_slug,
                zip_uris=[primary_zip_url],
                target_dir=target_dir,
                force=force,
                expected_sha256="",
                quiet=json_out,
            )
            installed_skills.append(skill_slug)
            if not json_out:
                print(f"  \u2713 {skill_slug}", file=sys.stderr)
        except SystemExit:
            failed_skills.append({"slug": skill_slug, "error": "install failed"})
            if not json_out:
                print(f"  \u2717 {skill_slug} (failed)", file=sys.stderr)

    # Install each skillset's orchestration prompt as skills/<skillset-slug>/SKILL.md
    # so that the Agent can discover and use the workflow prompt.
    installed_skillsets: List[str] = []
    for ss_slug, ss_prompt in skillset_prompts.items():
        ss_dir = install_root / ss_slug
        ss_skill_md = ss_dir / "SKILL.md"
        if ss_skill_md.exists() and not force:
            if not json_out:
                print(f"  \u229c {ss_slug} (skillset prompt already installed, skip)", file=sys.stderr)
            installed_skillsets.append(ss_slug)
            continue
        ss_dir.mkdir(parents=True, exist_ok=True)
        ss_skill_md.write_text(ss_prompt, encoding="utf-8")
        installed_skillsets.append(ss_slug)
        if not json_out:
            print(f"  \u2713 {ss_slug} (skillset prompt installed)", file=sys.stderr)

    # Install SOUL.md to the parent directory of install_root (workspace root)
    if soul_md:
        soul_path = install_root.parent / "SOUL.md"
        if soul_path.exists() and not force:
            if not json_out:
                print(f"  \u229c SOUL.md (already exists, skip)", file=sys.stderr)
        else:
            soul_path.write_text(soul_md, encoding="utf-8")
            if not json_out:
                print(f"  \u2713 SOUL.md installed to {soul_path}", file=sys.stderr)

    # Update lockfile with pack info
    lock = load_lockfile(install_root)
    installed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    packs = lock.setdefault("packs", {})

    # Record each skillset as a pack entry
    for ss_slug, ss_skills in skillset_skill_map.items():
        packs[ss_slug] = {
            "displayName": next(
                (ss.get("displayName", ss_slug) for ss in manifest.get("skillSets", []) if ss.get("slug") == ss_slug),
                manifest.get("displayName", ss_slug),
            ),
            "version": pack_version,
            "skillSlugs": ss_skills,
            "installedAt": installed_at,
        }

    # Record soul info if present
    soul_info = manifest.get("soul")
    if soul_info and isinstance(soul_info, dict):
        lock.setdefault("soul", {}).update({
            "slug": soul_info.get("slug", ""),
            "displayName": soul_info.get("displayName", ""),
            "installedAt": installed_at,
        })

    # Mark each successfully installed skill in skills lock
    skills_lock = lock.setdefault("skills", {})
    for s in installed_skills:
        if s not in skills_lock:
            # Find which skillset this skill belongs to
            source_pack = slug
            for ss_slug, ss_skills in skillset_skill_map.items():
                if s in ss_skills:
                    source_pack = ss_slug
                    break
            skills_lock[s] = {
                "name": s,
                "source": f"pack:{source_pack}",
                "version": "",
                "installedAt": installed_at,
            }
    save_lockfile(install_root, lock)

    if json_out:
        print(json.dumps({
            "success": len(failed_skills) == 0,
            "slug": slug,
            "displayName": manifest.get("displayName", manifest.get("soul", {}).get("displayName", slug)),
            "version": pack_version,
            "skillSets": list(skillset_skill_map.keys()),
            "skillSlugs": all_skill_slugs,
            "installed": installed_skills,
            "installedSkillSets": installed_skillsets,
            "failed": failed_skills,
            "installedAt": installed_at,
        }))
    else:
        total = len(all_skill_slugs)
        ok = len(installed_skills)
        fail = len(failed_skills)
        ss_count = len(installed_skillsets)
        print(f"\u2713 Skill pack '{slug}' installed ({ok}/{total} skills, {ss_count} skillset prompts)", end="")
        if fail > 0:
            print(f" [{fail} failed]", end="")
        print()


def _install_enterprise_skill(
    args: argparse.Namespace, org_slug: str, slug: str, version: Optional[str],
    *, json_out: bool = False,
) -> None:
    """安装企业技能: @org/slug[@version]"""
    # 优先级: --secret flag > SKILLHUB_SECRET env > stored credentials
    secret = getattr(args, "secret", None) or os.environ.get("SKILLHUB_SECRET")

    if secret:
        # Direct download with secret key (no login required)
        if not secret.startswith("sk-ent-"):
            if json_out:
                print(json.dumps({"success": False, "slug": slug, "error": "--secret must be an enterprise API key (sk-ent-...)"}))
                raise SystemExit(1)
            die("--secret must be an enterprise API key (sk-ent-...)")
        host = os.environ.get("SKILLHUB_HOST", DEFAULT_ENTERPRISE_HOST)
        # Resolve org_id via verify endpoint
        try:
            org_info = verify_api_key(host, secret)
        except RuntimeError as exc:
            if json_out:
                print(json.dumps({"success": False, "slug": slug, "error": f"API key verification failed: {exc}"}))
                raise SystemExit(1)
            die(f"API key verification failed: {exc}")
        org_id = org_info.get("orgId")
        api_key = secret
    else:
        # Existing credential flow
        env_cred = resolve_org_credential_from_env()
        if env_cred and (env_cred.get("orgOrgId") == org_slug or env_cred.get("orgSlug") == org_slug):
            cred = env_cred
        else:
            cred = get_org_credential(org_slug)

        if not cred:
            err_msg = (
                f"Not logged in to @{org_slug}. "
                f"Run: skillhub login --key <your-api-key> "
                f"Or use: skillhub install @{org_slug}/{slug} --secret <your-api-key>"
            )
            if json_out:
                print(json.dumps({"success": False, "slug": slug, "error": err_msg}))
                raise SystemExit(1)
            die(
                f"Not logged in to @{org_slug}.\n"
                f"  Run: skillhub login --key <your-api-key>\n"
                f"  Or use: skillhub install @{org_slug}/{slug} --secret <your-api-key>"
            )

        host = cred.get("host", DEFAULT_ENTERPRISE_HOST)
        org_id = cred.get("orgId")
        api_key = cred.get("apiKey", "")

        if not org_id or not api_key:
            if json_out:
                print(json.dumps({"success": False, "slug": slug, "error": f"Invalid credentials for @{org_slug}. Run: skillhub login --key <your-api-key>"}))
                raise SystemExit(1)
            die(
                f"Invalid credentials for @{org_slug}.\n"
                f"  Run: skillhub login --key <your-api-key>"
            )

    install_root = Path(args.dir).expanduser().resolve()
    target_dir = install_root / slug

    # 同名冲突检测：如果已安装的是不同来源的技能，自动覆盖并提示
    lock = load_lockfile(install_root)
    skills_lock = lock.setdefault("skills", {})
    existing = skills_lock.get(slug)
    force = args.force
    if existing:
        old_source = existing.get("source", "community")
        if old_source != f"@{org_slug}":
            old_version = existing.get("version", "?")
            if not json_out:
                print(
                    f"\u26a0\ufe0f  Replacing existing skill \"{slug}\" ({old_source} v{old_version}) "
                    f"with @{org_slug}/{slug}",
                    file=sys.stderr,
                )
            force = True

    # 下载企业技能
    try:
        installed_version = download_enterprise_skill(
            host=host,
            org_id=org_id,
            api_key=api_key,
            slug=slug,
            version=version,
            target_dir=target_dir,
            force=force,
        )
    except RuntimeError as exc:
        err_msg = f"Failed to install @{org_slug}/{slug}: {exc}"
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": err_msg}))
            raise SystemExit(1)
        die(err_msg)

    if installed_version is None:
        if version:
            err_msg = f'Skill "{slug}" version "{version}" not found in @{org_slug}.'
        else:
            err_msg = f'Skill "{slug}" not found in @{org_slug}. Run: skillhub search "{slug}" to find available skills.'
        if json_out:
            print(json.dumps({"success": False, "slug": slug, "error": err_msg}))
            raise SystemExit(1)
        if version:
            die(f'Skill "{slug}" version "{version}" not found in @{org_slug}.')
        else:
            die(f'Skill "{slug}" not found in @{org_slug}.\n  Run: skillhub search "{slug}" to find available skills.')

    # 更新 lockfile
    installed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    skills_lock[slug] = {
        "name": slug,
        "source": f"@{org_slug}",
        "org": org_slug,
        "host": host,
        "version": installed_version,
        "installedAt": installed_at,
    }
    save_lockfile(install_root, lock)
    update_clawhub_lock_v1(slug, installed_version)

    version_display = f"@{installed_version}" if installed_version != "latest" else ""
    if json_out:
        print(json.dumps({
            "success": True,
            "slug": slug,
            "name": slug,
            "version": installed_version,
            "source": f"@{org_slug}",
            "org": org_slug,
            "installedAt": installed_at,
            "targetDir": str(target_dir),
        }))
    else:
        print(f"\u2713 Installed: @{org_slug}/{slug}{version_display} -> {target_dir}")


def cmd_upgrade(args: argparse.Namespace) -> None:
    code = run_skills_upgrade(
        args,
        {
            "load_lockfile": load_lockfile,
            "save_lockfile": save_lockfile,
            "read_json_from_uri": read_json_from_uri,
            "extract_update_manifest_info": extract_update_manifest_info,
            "resolve_uri_with_base": resolve_uri_with_base,
            "version_is_newer": version_is_newer,
            "install_zip_to_target": install_zip_to_target,
            "skill_config_name": SKILL_CONFIG_NAME,
            "skill_meta_name": SKILL_META_NAME,
        },
    )
    if code != 0:
        raise SystemExit(code)


def cmd_self_upgrade(args: argparse.Namespace) -> None:
    config_path = Path(args.config).expanduser().resolve()
    target_path = Path(args.target).expanduser().resolve() if args.target else Path(__file__).resolve()
    try:
        upgraded, current_version, latest_version = run_self_upgrade_flow(
            config_path=config_path,
            target_path=target_path,
            current_version=args.current_version or CLI_VERSION,
            timeout=args.timeout,
            check_only=args.check_only,
            quiet=False,
        )
    except Exception as exc:
        die(str(exc))

    if upgraded:
        # User explicitly upgraded; any previously persisted ignore marker is stale.
        clear_ignored_self_update_version(config_path)
    if not upgraded and not args.check_only:
        print(f"CLI is up-to-date: current={current_version} latest={latest_version}")


def run_self_upgrade_flow(
    config_path: Path,
    target_path: Path,
    current_version: str,
    timeout: int,
    check_only: bool,
    quiet: bool,
) -> Tuple[bool, str, str]:
    manifest_url = resolve_self_update_manifest_url(config_path)
    verbose_log(f"fetching manifest: {manifest_url} (timeout={timeout}s)")
    manifest = read_json_from_uri(manifest_url, timeout=timeout)
    latest_version, package_uri_raw, expected_sha = extract_update_manifest_info(manifest)
    if not latest_version:
        raise RuntimeError(f"Self-update manifest missing version: {manifest_url}")
    if not package_uri_raw:
        raise RuntimeError(f"Self-update manifest missing package URL: {manifest_url}")

    current = normalize_version_text(current_version or CLI_VERSION)
    latest = normalize_version_text(latest_version)
    verbose_log(f"version compare: current={current} latest={latest}")
    if not version_is_newer(latest, current):
        verbose_log("no upgrade needed")
        return False, current, latest

    package_uri = resolve_uri_with_base(package_uri_raw, config_path.parent)
    verbose_log(f"resolved package URI: {package_uri}")
    if not quiet:
        print(
            f"Self-upgrade available: current={current} latest={latest}\n"
            f"Manifest: {manifest_url}\n"
            f"Package:  {package_uri}\n"
            f"Target:   {target_path}"
        )
    if check_only:
        verbose_log("check-only mode; skip install")
        return False, current, latest

    with tempfile.TemporaryDirectory(prefix="skillhub-self-upgrade-") as tmp:
        package_path = Path(tmp) / "package.bin"
        verbose_log(f"downloading package to temp: {package_path}")
        download_file_or_raise(package_uri, package_path)

        if expected_sha:
            verbose_log("sha256 present; verifying package checksum")
            actual_sha = sha256_file(package_path).lower()
            if actual_sha != expected_sha:
                raise RuntimeError(f"Self-upgrade SHA256 mismatch: expected {expected_sha}, got {actual_sha}")
        else:
            verbose_log("sha256 empty/missing; skip checksum verification")

        source_script: Path
        source_upgrade_module = None  # type: Optional[Path]
        source_version_file = None  # type: Optional[Path]
        source_metadata_file = None  # type: Optional[Path]
        source_find_skill_template = None  # type: Optional[Path]
        source_preference_skill_template = None  # type: Optional[Path]
        if zipfile.is_zipfile(package_path):
            extract_dir = Path(tmp) / "extract"
            extract_dir.mkdir(parents=True, exist_ok=True)
            safe_extract_zip(package_path, extract_dir)
            found = find_cli_script_in_extracted(extract_dir)
            if not found:
                raise RuntimeError("Self-upgrade zip does not contain skills_store_cli.py")
            source_script = found
            source_upgrade_module = find_peer_file_in_extracted(extract_dir, "skills_upgrade.py")
            source_version_file = find_peer_file_in_extracted(extract_dir, CLI_VERSION_FILE_NAME)
            source_metadata_file = find_peer_file_in_extracted(extract_dir, CLI_METADATA_FILE_NAME)
            source_find_skill_template = find_skill_file_in_extracted(extract_dir, "SKILL.md")
            source_preference_skill_template = find_skill_file_in_extracted(
                extract_dir,
                "SKILL.skillhub-preference.md",
            )
        elif tarfile.is_tarfile(package_path):
            extract_dir = Path(tmp) / "extract"
            extract_dir.mkdir(parents=True, exist_ok=True)
            safe_extract_tar(package_path, extract_dir)
            found = find_cli_script_in_extracted(extract_dir)
            if not found:
                raise RuntimeError("Self-upgrade tar package does not contain skills_store_cli.py")
            source_script = found
            source_upgrade_module = find_peer_file_in_extracted(extract_dir, "skills_upgrade.py")
            source_version_file = find_peer_file_in_extracted(extract_dir, CLI_VERSION_FILE_NAME)
            source_metadata_file = find_peer_file_in_extracted(extract_dir, CLI_METADATA_FILE_NAME)
            source_find_skill_template = find_skill_file_in_extracted(extract_dir, "SKILL.md")
            source_preference_skill_template = find_skill_file_in_extracted(
                extract_dir,
                "SKILL.skillhub-preference.md",
            )
        else:
            source_script = package_path

        try:
            raw = source_script.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise RuntimeError(f"Self-upgrade package is not a text python script: {exc}") from exc
        if "def main()" not in raw:
            raise RuntimeError("Self-upgrade package content check failed (missing def main())")

        backup_path = target_path.with_suffix(target_path.suffix + ".bak")
        if target_path.exists():
            verbose_log(f"writing backup: {backup_path}")
            shutil.copyfile(target_path, backup_path)
        verbose_log(f"replacing target script: {target_path}")
        shutil.copyfile(source_script, target_path)
        target_path.chmod(0o755)

        target_upgrade_module = target_path.parent / "skills_upgrade.py"
        if source_upgrade_module and source_upgrade_module.exists():
            verbose_log(f"updating companion module: {target_upgrade_module}")
            shutil.copyfile(source_upgrade_module, target_upgrade_module)

        target_metadata_file = target_path.parent / CLI_METADATA_FILE_NAME
        if source_metadata_file and source_metadata_file.exists():
            verbose_log(f"updating metadata file from package: {target_metadata_file}")
            shutil.copyfile(source_metadata_file, target_metadata_file)

        version_file_path = target_path.parent / CLI_VERSION_FILE_NAME
        if source_version_file and source_version_file.exists():
            verbose_log(f"updating version file from package: {version_file_path}")
            shutil.copyfile(source_version_file, version_file_path)
        else:
            verbose_log(f"updating version file: {version_file_path} -> {latest}")
            version_file_path.write_text(
                json.dumps({"version": latest}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        try:
            run_post_upgrade_plugin_migration(
                latest_version=latest,
                find_skill_template=source_find_skill_template,
                preference_skill_template=source_preference_skill_template,
            )
        except Exception as exc:
            verbose_log(f"post-upgrade migration failed; continue: {exc}")
        if not quiet:
            print(f"Self-upgrade complete: {target_path} -> version {latest}")
            print(f"Backup saved at: {backup_path}")
    return True, current, latest


def startup_self_upgrade_check(config_path: Optional[Path] = None) -> bool:
    if config_path is None:
        config_path = Path(f"{DEFAULT_CLI_HOME}/{CLI_CONFIG_NAME}").expanduser().resolve()
    if not config_path.exists():
        verbose_log(f"startup check: config not found at {config_path}; will use default manifest")
    try:
        upgraded, _, _ = run_self_upgrade_flow(
            config_path=config_path,
            target_path=Path(__file__).resolve(),
            current_version=CLI_VERSION,
            timeout=SELF_UPGRADE_CHECK_TIMEOUT_SECONDS,
            check_only=False,
            quiet=True,
        )
        verbose_log(f"startup check result: upgraded={upgraded}")
        return upgraded
    except BaseException:
        verbose_log("startup check failed; continue without upgrade")
        return False


def is_interactive_terminal() -> bool:
    """Strict TTY check: both stdin and stdout must be a real terminal."""
    try:
        return bool(sys.stdin.isatty() and sys.stdout.isatty())
    except Exception:
        return False


def read_ignored_self_update_version(config_path: Path) -> str:
    if not config_path.exists():
        return ""
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    if not isinstance(raw, dict):
        return ""
    value = raw.get(IGNORED_SELF_UPDATE_VERSION_KEY)
    if isinstance(value, str):
        return value.strip()
    return ""


def write_ignored_self_update_version(config_path: Path, version: str) -> None:
    """Persist ignored version into ~/.skillhub/config.json (merging existing fields)."""
    raw: Dict[str, Any] = {}
    if config_path.exists():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                raw = loaded
        except (json.JSONDecodeError, OSError):
            raw = {}
    raw[IGNORED_SELF_UPDATE_VERSION_KEY] = version.strip()
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(raw, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        verbose_log(f"persisted ignored_self_update_version={version} -> {config_path}")
    except OSError as exc:
        verbose_log(f"failed to persist ignored version: {exc}")


def clear_ignored_self_update_version(config_path: Path) -> None:
    """Remove ignored marker once we've upgraded past it (best-effort)."""
    if not config_path.exists():
        return
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    if not isinstance(raw, dict):
        return
    if IGNORED_SELF_UPDATE_VERSION_KEY not in raw:
        return
    raw.pop(IGNORED_SELF_UPDATE_VERSION_KEY, None)
    try:
        config_path.write_text(
            json.dumps(raw, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        verbose_log(f"cleared ignored_self_update_version from {config_path}")
    except OSError as exc:
        verbose_log(f"failed to clear ignored version: {exc}")


def _prompt_self_upgrade_choice(current: str, latest: str) -> str:
    """Ask the user via stderr/stdin. Returns 'yes', 'no', or 'skip' (EOF/error)."""
    forced = os.environ.get(SELF_UPGRADE_PROMPT_ANSWER_ENV, "").strip().lower()
    if forced in ("y", "yes", "true", "1"):
        return "yes"
    if forced in ("n", "no", "false", "0"):
        return "no"
    if forced in ("skip", "abort", "cancel"):
        return "skip"

    try:
        sys.stderr.write(
            f"发现 SkillHub CLI 新版本 {latest}，当前版本 {current}，是否升级？[Y/n] "
        )
        sys.stderr.flush()
        answer = sys.stdin.readline()
    except (EOFError, KeyboardInterrupt, OSError):
        sys.stderr.write("\n")
        return "skip"

    if not answer:
        # readline returns "" on EOF
        return "skip"
    normalized = answer.strip().lower()
    if normalized in ("", "y", "yes"):
        return "yes"
    if normalized in ("n", "no"):
        return "no"
    # Treat unknown answers as "no this time", but don't persist ignore.
    return "skip"


def startup_self_upgrade_prompt(
    config_path: Path,
    *,
    allow_interactive_prompt: bool = True,
) -> bool:
    """New prompt-based startup self-upgrade flow.

    Behavior:
    - Fetch manifest with short timeout.
    - If no newer version: do nothing.
    - If user previously ignored exactly this version: do nothing.
    - Interactive TTY: ask Y/n. yes -> upgrade & re-exec; no -> persist ignore.
    - Non-interactive / machine-readable callers: auto-upgrade quietly.
    - Non-interactive upgrade failure is best-effort and does not block the command.
    Returns True only when an upgrade actually happened (so caller can re-exec).
    """
    try:
        manifest_url = resolve_self_update_manifest_url(config_path)
        verbose_log(f"prompt check: fetching manifest {manifest_url}")
        manifest = read_json_from_uri(
            manifest_url, timeout=SELF_UPGRADE_CHECK_TIMEOUT_SECONDS
        )
        latest_version, _package_uri_raw, _expected_sha = extract_update_manifest_info(manifest)
    except BaseException as exc:  # noqa: BLE001
        verbose_log(f"prompt check: manifest fetch failed: {exc}")
        return False

    if not latest_version:
        verbose_log("prompt check: manifest missing version field")
        return False

    current = normalize_version_text(CLI_VERSION)
    latest = normalize_version_text(latest_version)
    if not version_is_newer(latest, current):
        verbose_log(f"prompt check: up-to-date current={current} latest={latest}")
        return False

    ignored = read_ignored_self_update_version(config_path)
    if ignored and normalize_version_text(ignored) == latest:
        verbose_log(f"prompt check: version {latest} previously ignored; skip")
        return False

    if not allow_interactive_prompt or not is_interactive_terminal():
        verbose_log("prompt check: non-interactive path; auto-upgrade quietly")
        try:
            upgraded, _, _ = run_self_upgrade_flow(
                config_path=config_path,
                target_path=Path(__file__).resolve(),
                current_version=CLI_VERSION,
                timeout=max(SELF_UPGRADE_CHECK_TIMEOUT_SECONDS, 20),
                check_only=False,
                quiet=True,
            )
        except BaseException as exc:  # noqa: BLE001
            verbose_log(f"non-interactive auto-upgrade failed; continue: {exc}")
            return False
        if upgraded:
            clear_ignored_self_update_version(config_path)
        return upgraded

    choice = _prompt_self_upgrade_choice(current, latest)
    if choice == "no":
        write_ignored_self_update_version(config_path, latest)
        try:
            sys.stderr.write(
                f"[skillhub] 已记住忽略版本 {latest}。"
                f"如需升级，运行 `skillhub self-upgrade`。\n"
            )
            sys.stderr.flush()
        except OSError:
            pass
        return False
    if choice != "yes":
        # skip / EOF / unknown answer -> do nothing this run
        verbose_log(f"prompt check: user choice='{choice}'; skip upgrade")
        return False

    # User accepted: perform the actual upgrade (non-quiet so they see progress).
    try:
        upgraded, _, _ = run_self_upgrade_flow(
            config_path=config_path,
            target_path=Path(__file__).resolve(),
            current_version=CLI_VERSION,
            timeout=max(SELF_UPGRADE_CHECK_TIMEOUT_SECONDS, 20),
            check_only=False,
            quiet=False,
        )
    except BaseException as exc:  # noqa: BLE001
        try:
            sys.stderr.write(f"[skillhub] 自升级失败：{exc}\n")
            sys.stderr.flush()
        except OSError:
            pass
        return False

    if upgraded:
        # Drop a stale ignore marker (best-effort).
        clear_ignored_self_update_version(config_path)
    return upgraded


def cmd_list(args: argparse.Namespace) -> None:
    install_root = Path(args.dir).expanduser().resolve()
    lock = load_lockfile(install_root)
    skills = lock.get("skills", {})
    if not skills:
        print("No installed skills.")
        return
    for slug, meta in sorted(skills.items()):
        if isinstance(meta, dict):
            version = str(meta.get("version", "")).strip()
            print(f"{slug}  {version}")
        else:
            print(f"{slug}  ")


# ============================================================
# Skill 评论区 —— comment subcommands（先发布后审核）
# ============================================================


def _comment_http_json(
    method: str,
    url: str,
    token: Optional[str],
    payload: Optional[Dict[str, Any]] = None,
    *,
    timeout: int = 15,
) -> Tuple[int, Dict[str, Any]]:
    """通用评论接口请求：发送 method 请求到 url，返回 (status_code, json_body)。

    - token 非空时携带 Authorization: Bearer；payload 非空时以 JSON body 发送。
    - HTTP 4xx/5xx 不抛异常，而是返回其状态码与响应体，交由调用方转中文提示。
    - 网络错误抛 RuntimeError。
    """
    data: Optional[bytes] = None
    headers = cli_request_headers({"Accept": "application/json"})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - 仅访问用户配置的 host
            body = resp.read()
            parsed: Dict[str, Any] = {}
            if body:
                try:
                    parsed = json.loads(body.decode("utf-8") or "{}")
                except json.JSONDecodeError:
                    parsed = {}
            return resp.getcode(), parsed
    except urllib.error.HTTPError as exc:
        body_bytes = b""
        try:
            body_bytes = exc.read() or b""
        except Exception:
            body_bytes = b""
        parsed = {}
        if body_bytes:
            try:
                parsed = json.loads(body_bytes.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                parsed = {"error": body_bytes.decode("utf-8", errors="replace")[:300]}
        return exc.code, parsed
    except urllib.error.URLError as exc:
        raise RuntimeError(f"网络错误: {exc.reason}") from exc


def _comment_status_hint(status: int, body: Dict[str, Any]) -> str:
    """把 HTTP 错误码转为可读中文提示。"""
    err = str(body.get("error") or "").strip()
    mapping = {
        400: "请求参数不合法（内容为空且无图片/超过 500 字/图片超 9 张/图片 URL 非法）",
        401: "未登录，请先执行: skillhub login --key skh_xxx",
        403: "无权限操作该评论（仅作者 / Skill 拥有者 / 管理员可删除）",
        404: "Skill 或评论不存在",
        429: "操作过于频繁，请 10 秒后重试",
    }
    base = mapping.get(status, f"HTTP {status}")
    if err:
        return f"{base}（{err}）"
    return base


def _slug_namespace_from_args(args: argparse.Namespace) -> Tuple[str, str]:
    raw_slug = str(getattr(args, "slug", "") or "").strip()
    namespace = normalize_namespace_arg(getattr(args, "namespace", ""))
    if raw_slug.startswith("@"):
        try:
            parsed_namespace, parsed_slug, parsed_version = parse_skill_ref(raw_slug)
        except ValueError as exc:
            die(str(exc))
        if parsed_version:
            die("该命令不支持在 slug 中指定 version")
        if namespace and parsed_namespace and namespace != parsed_namespace:
            die("请不要同时使用 @namespace/slug 和 --namespace，或确保两者一致")
        namespace = namespace or normalize_namespace_arg(parsed_namespace)
        raw_slug = parsed_slug
    if not raw_slug:
        die("missing slug")
    return raw_slug, namespace


def _comment_api_base(host: str, slug: str) -> str:
    return host.rstrip("/") + f"/api/v1/skills/{urllib.parse.quote(slug, safe='')}/comments"


# 评论图片/表情包上传：仅允许 jpeg/png/webp，单张 <=5MB，单条评论 <=9 张（与后端约束一致）。
_COMMENT_IMAGE_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
_COMMENT_IMAGE_MAX_BYTES = 5 * 1024 * 1024
_COMMENT_MAX_IMAGES = 9


def _comment_upload_image(
    host: str,
    slug: str,
    namespace: str,
    token: Optional[str],
    path: str,
    *,
    timeout: int = 30,
) -> str:
    """上传单张评论图片/表情包到 COS，返回可访问 URL；失败抛 RuntimeError。"""
    p = Path(path).expanduser()
    if not p.is_file():
        raise RuntimeError(f"图片文件不存在: {path}")
    mime = _COMMENT_IMAGE_MIME.get(p.suffix.lower())
    if not mime:
        raise RuntimeError(f"不支持的图片格式: {p.suffix or path}（仅 jpeg/png/webp）")
    data = p.read_bytes()
    if not data:
        raise RuntimeError(f"图片为空: {path}")
    if len(data) > _COMMENT_IMAGE_MAX_BYTES:
        raise RuntimeError(f"图片过大（>5MB）: {path}")

    boundary = "----skillhubCLI" + base64.urlsafe_b64encode(os.urandom(12)).decode("ascii").rstrip("=")
    filename = p.name.replace('"', "").replace("\r", "").replace("\n", "")
    pre = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode("utf-8")
    tail = f"\r\n--{boundary}--\r\n".encode("utf-8")
    body = pre + data + tail

    url = append_query_params(_comment_api_base(host, slug) + "/images", {"namespace": namespace})
    headers = cli_request_headers({
        "Accept": "application/json",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    })
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - 仅访问用户配置的 host
            parsed = json.loads((resp.read() or b"{}").decode("utf-8") or "{}")
            uploaded = str(parsed.get("url") or "").strip()
            if not uploaded:
                raise RuntimeError("图片上传成功但未返回 URL")
            return uploaded
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = (exc.read() or b"").decode("utf-8", errors="replace")[:200]
        except Exception:
            detail = ""
        raise RuntimeError(f"图片上传失败 (HTTP {exc.code}) {detail}".strip()) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"网络错误: {exc.reason}") from exc


def _upload_comment_images(host: str, slug: str, namespace: str, token: Optional[str], paths: List[str]) -> List[str]:
    """批量上传图片，返回 URL 列表；任一失败即 die。"""
    if len(paths) > _COMMENT_MAX_IMAGES:
        die(f"单条评论最多 {_COMMENT_MAX_IMAGES} 张图片")
    urls: List[str] = []
    for path in paths:
        try:
            urls.append(_comment_upload_image(host, slug, namespace, token, path))
        except RuntimeError as exc:
            die(str(exc))
    return urls


def _format_comment_line(c: Dict[str, Any], indent: str = "") -> str:
    status = c.get("status", "")
    content = c.get("content", "")
    if status == "removed":
        content = "（该评论已删除）"
    reply_to = c.get("replyToUserId") or 0
    who = f" 回复 uid={reply_to}" if reply_to else ""
    images = c.get("imageUrls") or []
    img_suffix = f"  [图片 x{len(images)}]" if images else ""
    like_count = int(c.get("likeCount") or 0)
    liked = bool(c.get("liked"))
    like_marker = "♥" if liked else "♡"
    like_suffix = f" {like_marker}{like_count}"
    return (
        f"{indent}#{c.get('id')} [uid={c.get('userId')}{who}] "
        f"audit={c.get('auditStatus', '-')} status={status}{like_suffix}\n"
        f"{indent}  {content}{img_suffix}"
    )


def cmd_comment_post(args: argparse.Namespace) -> None:
    """skillhub comment post <slug> [--content "..."] [--image PATH ...]"""
    token, host = resolve_user_token(args)
    slug, namespace = _slug_namespace_from_args(args)
    content = (args.content or "").strip()
    images = list(getattr(args, "image", None) or [])
    if not content and not images:
        die("--content 与 --image 至少提供其一")
    image_urls = _upload_comment_images(host, slug, namespace, token, images)
    payload: Dict[str, Any] = {"content": content}
    if image_urls:
        payload["imageUrls"] = image_urls
    url = append_query_params(_comment_api_base(host, slug), {"namespace": namespace})
    try:
        status, body = _comment_http_json("POST", url, token, payload)
    except RuntimeError as exc:
        die(str(exc))
    if status not in (200, 201):
        die(_comment_status_hint(status, body))
    if getattr(args, "json_output", False):
        print(json.dumps(body, ensure_ascii=False))
        return
    print(f"\u2713 已发表评论 #{body.get('id')}（审核状态: {body.get('auditStatus', 'pending')}）")


def cmd_comment_reply(args: argparse.Namespace) -> None:
    """skillhub comment reply <slug> <commentID> [--content "..."] [--image PATH ...]"""
    token, host = resolve_user_token(args)
    slug, namespace = _slug_namespace_from_args(args)
    content = (args.content or "").strip()
    images = list(getattr(args, "image", None) or [])
    if not content and not images:
        die("--content 与 --image 至少提供其一")
    image_urls = _upload_comment_images(host, slug, namespace, token, images)
    payload: Dict[str, Any] = {"content": content}
    if image_urls:
        payload["imageUrls"] = image_urls
    url = append_query_params(
        _comment_api_base(host, slug) + f"/{int(args.comment_id)}/replies",
        {"namespace": namespace},
    )
    try:
        status, body = _comment_http_json("POST", url, token, payload)
    except RuntimeError as exc:
        die(str(exc))
    if status not in (200, 201):
        die(_comment_status_hint(status, body))
    if getattr(args, "json_output", False):
        print(json.dumps(body, ensure_ascii=False))
        return
    print(f"\u2713 已回复评论 #{args.comment_id} -> 新回复 #{body.get('id')}（审核状态: {body.get('auditStatus', 'pending')}）")


def cmd_comment_list(args: argparse.Namespace) -> None:
    """skillhub comment list <slug> [--sort new|hot] [--cursor N | --offset N] [--limit N] [--json]

    - sort=new（默认）：按 created_at DESC 游标分页（--cursor 传上一页 nextCursor）。
    - sort=hot：按 like_count DESC，offset/limit 翻页（--offset 上限 1000，nextCursor 恒为 null）。
    """
    token, host = resolve_user_token_optional(args)
    slug, namespace = _slug_namespace_from_args(args)
    sort = (getattr(args, "sort", None) or "new").lower().strip()
    if sort not in ("new", "hot"):
        die("--sort 只能是 new 或 hot")
    params = [f"sort={sort}"]
    if sort == "hot":
        offset = int(getattr(args, "offset", 0) or 0)
        if offset < 0:
            offset = 0
        if offset:
            params.append(f"offset={offset}")
    else:
        if getattr(args, "cursor", 0):
            params.append(f"cursor={int(args.cursor)}")
    if getattr(args, "limit", 0):
        params.append(f"limit={int(args.limit)}")
    url = append_query_params(
        _comment_api_base(host, slug),
        {"namespace": namespace, **dict(urllib.parse.parse_qsl("&".join(params)))},
    )
    try:
        status, body = _comment_http_json("GET", url, token)
    except RuntimeError as exc:
        die(str(exc))
    if status != 200:
        die(_comment_status_hint(status, body))
    if getattr(args, "json_output", False):
        print(json.dumps(body, ensure_ascii=False))
        return
    total = body.get("total", 0)
    items = body.get("items", []) or []
    print(f"共 {total} 条一级评论（sort={sort}）：")
    for item in items:
        print(_format_comment_line(item))
        replies = (item.get("replies") or {})
        preview = replies.get("preview", []) or []
        rtotal = replies.get("total", 0)
        for rep in preview:
            print(_format_comment_line(rep, indent="    "))
        if rtotal > len(preview):
            print(f"    ... 还有 {rtotal - len(preview)} 条回复，用 comment replies-more 查看")
    nxt = body.get("nextCursor")
    if sort == "hot":
        # hot 模式无 cursor，用 --offset 翻页提示。
        next_offset = int(getattr(args, "offset", 0) or 0) + len(items)
        if len(items) == (int(getattr(args, "limit", 0) or 20)) and next_offset < 1000:
            print(f"下一页: --offset {next_offset}")
    elif nxt:
        print(f"下一页游标: --cursor {nxt}")


def cmd_comment_replies_more(args: argparse.Namespace) -> None:
    """skillhub comment replies-more <slug> <commentID> [--cursor] [--limit] [--json]"""
    token, host = resolve_user_token_optional(args)
    slug, namespace = _slug_namespace_from_args(args)
    params = {"namespace": namespace}
    if getattr(args, "cursor", 0):
        params["cursor"] = int(args.cursor)
    if getattr(args, "limit", 0):
        params["limit"] = int(args.limit)
    url = append_query_params(_comment_api_base(host, slug) + f"/{int(args.comment_id)}/replies", params)
    try:
        status, body = _comment_http_json("GET", url, token)
    except RuntimeError as exc:
        die(str(exc))
    if status != 200:
        die(_comment_status_hint(status, body))
    if getattr(args, "json_output", False):
        print(json.dumps(body, ensure_ascii=False))
        return
    items = body.get("items", []) or []
    print(f"评论 #{args.comment_id} 的回复（本页 {len(items)} 条）：")
    for rep in items:
        print(_format_comment_line(rep, indent="  "))
    nxt = body.get("nextCursor")
    if nxt:
        print(f"下一页游标: --cursor {nxt}")


def cmd_comment_delete(args: argparse.Namespace) -> None:
    """skillhub comment delete <slug> <commentID>"""
    token, host = resolve_user_token(args)
    slug, namespace = _slug_namespace_from_args(args)
    url = append_query_params(_comment_api_base(host, slug) + f"/{int(args.comment_id)}", {"namespace": namespace})
    try:
        status, body = _comment_http_json("DELETE", url, token)
    except RuntimeError as exc:
        die(str(exc))
    if status != 200:
        die(_comment_status_hint(status, body))
    if getattr(args, "json_output", False):
        print(json.dumps(body, ensure_ascii=False))
        return
    if body.get("deleted"):
        print(f"\u2713 已删除评论 #{args.comment_id}")
    else:
        print(f"评论 #{args.comment_id} 已处于删除状态（无需重复删除）")


def _cmd_comment_like_toggle(args: argparse.Namespace, like: bool) -> None:
    """点赞/取消点赞（幂等）。like=True 走 POST，False 走 DELETE。"""
    token, host = resolve_user_token(args)
    slug, namespace = _slug_namespace_from_args(args)
    url = append_query_params(
        _comment_api_base(host, slug) + f"/{int(args.comment_id)}/like",
        {"namespace": namespace},
    )
    method = "POST" if like else "DELETE"
    try:
        status, body = _comment_http_json(method, url, token)
    except RuntimeError as exc:
        die(str(exc))
    if status != 200:
        die(_comment_status_hint(status, body))
    if getattr(args, "json_output", False):
        print(json.dumps(body, ensure_ascii=False))
        return
    action = "点赞" if like else "取消点赞"
    changed = body.get("changed")
    like_count = body.get("likeCount", 0)
    if changed:
        print(f"\u2713 已{action}评论 #{args.comment_id}（当前 {like_count} 赞）")
    else:
        state = "已点赞" if like else "未点赞"
        print(f"评论 #{args.comment_id} 已处于「{state}」状态（当前 {like_count} 赞，幂等）")


def cmd_comment_like(args: argparse.Namespace) -> None:
    """skillhub comment like <slug> <commentID>"""
    _cmd_comment_like_toggle(args, like=True)


def cmd_comment_unlike(args: argparse.Namespace) -> None:
    """skillhub comment unlike <slug> <commentID>"""
    _cmd_comment_like_toggle(args, like=False)


def resolve_user_token_optional(args: argparse.Namespace) -> Tuple[Optional[str], str]:
    """与 resolve_user_token 类似，但 token 缺失时不报错（用于公开只读接口）。

    返回 (token_or_None, host)。
    """
    try:
        token, host = resolve_user_token(args)
        return token, host
    except SystemExit:
        # 未登录：公开接口无需 token，仅解析 host。
        host = (getattr(args, "host", None) or "").strip()
        if not host:
            cred = load_user_credential()
            if cred and cred.get("host"):
                host = str(cred["host"]).strip()
            else:
                host = os.environ.get("SKILLHUB_API_BASE", "").strip() or DEFAULT_ENTERPRISE_HOST
        return None, host


# ============================================================
# sandbox run —— SSE 在线调用 skill + 会话复用
# ============================================================


def run_sessions_path() -> Path:
    """返回 run 会话复用缓存路径: ~/.skillhub/run_sessions.json"""
    return Path(DEFAULT_CLI_HOME).expanduser() / RUN_SESSIONS_FILE_NAME


def _run_session_key(host: str, skills: List[str]) -> str:
    """复用分桶键 = host + 排序后的 skills 组合。换 host 或换 skills 组合即换桶。"""
    return host.rstrip("/") + "\n" + ",".join(sorted(skills))


def _load_run_sessions() -> Dict[str, Any]:
    """加载 run 会话缓存；文件不存在/损坏一律视为空。"""
    p = run_sessions_path()
    if not p.exists():
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_run_sessions(data: Dict[str, Any]) -> None:
    """原子写入 run 会话缓存（0600）。写失败静默忽略，不阻断主流程。"""
    p = run_sessions_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.chmod(str(tmp), 0o600)
        tmp.replace(p)
    except OSError:
        try:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            os.chmod(str(p), 0o600)
        except OSError:
            pass


def _run_status_hint(status: int, body: Dict[str, Any]) -> str:
    """把 sandbox run/session 接口的 HTTP 错误码转为可读中文提示。"""
    err = str(body.get("error") or "").strip()
    mapping = {
        400: "请求参数不合法",
        401: "未登录或 token 失效，请先执行: skillhub login --key skh_xxx",
        403: "无权限（会话属于其他用户）",
        404: "会话不存在或已关闭",
        409: "会话已关闭，不可写入",
        429: "调用过于频繁，请稍后重试",
        501: "服务端未启用 sandbox 能力",
        503: "sandbox 运行时暂不可用，请稍后重试",
    }
    base = mapping.get(status, f"HTTP {status}")
    return f"{base}（{err}）" if err else base


def _eprint_run(message: str) -> None:
    """把提示打到 stderr，保持 stdout 干净（只承载 agent 输出 / --json 结果）。"""
    print(f"[run] {message}", file=sys.stderr, flush=True)


def _create_run_session(host: str, token: str, skills: List[str], *, timeout: int = 120) -> str:
    """POST /api/v1/sandbox/sessions 建一个持久会话（不自动关闭），返回 session_id。

    这是「不改服务端」前提下唯一能拿到可跨次复用会话的现成入口；注意它会写用户
    「已安装 skill」列表、并出现在 Web 会话列表（纯 CLI 方案的固有副作用）。
    """
    url = host.rstrip("/") + "/api/v1/sandbox/sessions"
    payload: Dict[str, Any] = {}
    if skills:
        payload["skills"] = list(skills)
    try:
        status, body = _comment_http_json("POST", url, token, payload, timeout=timeout)
    except RuntimeError as exc:
        die(str(exc))
    if status not in (200, 201):
        die(_run_status_hint(status, body))
    sid = str(body.get("session_id") or "").strip()
    if not sid:
        die("创建会话失败：响应缺少 session_id")
    return sid


def _extract_agent_text(msg: Any) -> str:
    """从一条 agent JSON-RPC 通知里提取增量文本（agent_message_chunk）。

    与前端 parseStreamEvent 对齐：只渲染 session/update 里 sessionUpdate=
    agent_message_chunk 的 text 内容；其余（tool_call / artifact 等）在文本模式下忽略。
    """
    if not isinstance(msg, dict):
        return ""
    params = msg.get("params")
    if not isinstance(params, dict):
        return ""
    update = params.get("update")
    if not isinstance(update, dict):
        return ""
    if update.get("sessionUpdate") != "agent_message_chunk":
        return ""
    content = update.get("content")
    # cloudagent 的 content 形如 {"text": "<delta>"}，通常不带 type 字段；
    # content.text 是增量 delta（顺序拼接即完整回答）。兼容三种形态：
    #   1) {"text": "..."}（无 type）2) {"type":"text","text":"..."} 3) [ {...}, ... ]
    if isinstance(content, dict):
        t = content.get("text")
        return t if isinstance(t, str) else ""
    if isinstance(content, list):
        parts = [
            str(b.get("text"))
            for b in content
            if isinstance(b, dict) and isinstance(b.get("text"), str)
        ]
        return "".join(parts)
    return ""


def _dispatch_run_frame(event: Optional[str], data_str: str, result: Dict[str, Any], json_mode: bool) -> None:
    """解析一条 SSE 帧并更新 result / 渲染输出。"""
    data_str = data_str.strip()
    if not data_str:
        return
    try:
        obj = json.loads(data_str)
    except json.JSONDecodeError:
        return

    if event == "run_meta":
        if isinstance(obj, dict):
            result["meta"] = obj
        if json_mode:
            print(json.dumps({"run_meta": obj}, ensure_ascii=False), flush=True)
        return

    # 默认帧 = StreamEvent {type, data, tokens, error}
    if json_mode:
        print(json.dumps(obj, ensure_ascii=False), flush=True)
    if not isinstance(obj, dict):
        return
    etype = str(obj.get("type") or "")
    if etype == "message":
        if not json_mode:
            text = _extract_agent_text(obj.get("data"))
            if text:
                sys.stdout.write(text)
                sys.stdout.flush()
    elif etype in ("done", "error", "cancelled"):
        result["terminal"] = etype
        if obj.get("error"):
            result["error"] = str(obj.get("error"))
        try:
            result["tokens"] = int(obj.get("tokens") or 0)
        except (TypeError, ValueError):
            result["tokens"] = 0


def _stream_run(
    host: str,
    token: str,
    body: Dict[str, Any],
    *,
    json_mode: bool = False,
    timeout: int = 600,
) -> Dict[str, Any]:
    """POST /api/v1/sandbox/runs 读 SSE 流，实时渲染 agent 输出。

    返回 result dict:
      - terminal: "done" | "error" | "cancelled" | None（本轮终止类型）
      - http_status: int | None（SSE 头写出前的 HTTP 错误码，用于复用失效判定）
      - error: str | None
      - meta: dict（run_meta：session_id / ephemeral）
      - tokens: int
    """
    url = host.rstrip("/") + "/api/v1/sandbox/runs"
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = cli_request_headers({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "text/event-stream",
    })
    req = urllib.request.Request(url, data=data, method="POST", headers=headers)
    result: Dict[str, Any] = {
        "terminal": None,
        "http_status": None,
        "error": None,
        "meta": {},
        "tokens": 0,
    }

    try:
        resp = urllib.request.urlopen(req, timeout=timeout)  # nosec - 仅访问用户配置的 host
    except urllib.error.HTTPError as exc:
        body_bytes = b""
        try:
            body_bytes = exc.read() or b""
        except Exception:
            body_bytes = b""
        parsed: Dict[str, Any] = {}
        if body_bytes:
            try:
                parsed = json.loads(body_bytes.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                parsed = {"error": body_bytes.decode("utf-8", errors="replace")[:300]}
        result["http_status"] = exc.code
        result["error"] = str(parsed.get("error") or f"HTTP {exc.code}")
        return result
    except urllib.error.URLError as exc:
        result["error"] = f"网络错误: {exc.reason}"
        return result

    try:
        with resp:
            event: Optional[str] = None
            data_lines: List[str] = []
            for raw in resp:
                line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                if line == "":
                    # 空行 = 一帧结束
                    if data_lines or event is not None:
                        _dispatch_run_frame(event, "\n".join(data_lines), result, json_mode)
                    event = None
                    data_lines = []
                    if result["terminal"]:
                        break
                    continue
                if line.startswith(":"):
                    continue  # 注释 / keepalive 帧
                if line.startswith("event:"):
                    event = line[len("event:"):].strip()
                elif line.startswith("data:"):
                    data_lines.append(line[len("data:"):].lstrip())
            # flush 结尾未以空行收尾的残帧
            if not result["terminal"] and (data_lines or event is not None):
                _dispatch_run_frame(event, "\n".join(data_lines), result, json_mode)
    except (TimeoutError, OSError) as exc:
        if result["terminal"] is None:
            result["error"] = f"流式连接中断: {exc}"

    return result


def _is_session_closed_reason(err: Optional[str]) -> bool:
    """判断 error 文案是否指向「会话已失效」，用于复用失败后自动重建。"""
    if not err:
        return False
    low = str(err).lower()
    return (
        "no longer writable" in low
        or "closed" in low
        or "not found" in low
        or "不可写" in str(err)
    )


def cmd_run(args: argparse.Namespace) -> None:
    """skillhub run "<输入>" --skill ppt [--session ID] [--new] [--no-reuse] [--ttl S] [--json]

    SSE 在线调用 skill：一次请求建/复用一个沙箱会话 → 加载 skill → 流式回传 agent 输出。
    默认 30 分钟滑动窗口内，同一 skills 组合复用同一会话（缓存于 ~/.skillhub/run_sessions.json）。
    """
    token, host = resolve_user_token(args)
    skills = sorted({s.strip() for s in (getattr(args, "skill", None) or []) if s and s.strip()})

    raw_input = args.input
    if raw_input == "-":
        raw_input = sys.stdin.read()
    text = (raw_input or "").strip()
    if not text:
        die("缺少输入：提供 input 位置参数，或用 '-' 从 stdin 读取")

    json_mode = bool(getattr(args, "json_output", False))
    ttl = int(getattr(args, "ttl", DEFAULT_RUN_SESSION_TTL) or DEFAULT_RUN_SESSION_TTL)
    timeout = int(getattr(args, "timeout", 600) or 600)

    key = _run_session_key(host, skills)
    cache = _load_run_sessions()

    explicit_session = (getattr(args, "session", None) or "").strip()
    force_new = bool(getattr(args, "new", False))
    no_reuse = bool(getattr(args, "no_reuse", False))

    session_id = ""
    reused = False
    if explicit_session:
        session_id = explicit_session
        reused = True
    elif not force_new and not no_reuse:
        entry = cache.get(key)
        if isinstance(entry, dict):
            sid = str(entry.get("session_id") or "").strip()
            try:
                last_used = float(entry.get("last_used") or 0)
            except (TypeError, ValueError):
                last_used = 0.0
            if sid and (time.time() - last_used) < ttl:
                session_id = sid
                reused = True

    if not session_id:
        session_id = _create_run_session(host, token, skills, timeout=min(timeout, 120))
        reused = False
        _eprint_run(f"已创建会话 {session_id}")
    elif reused and not explicit_session:
        _eprint_run(f"复用会话 {session_id}")

    body: Dict[str, Any] = {"input": text, "session_id": session_id}
    if skills:
        body["skills"] = skills

    result = _stream_run(host, token, body, json_mode=json_mode, timeout=timeout)

    # 复用失败（会话失效）→ 清缓存、重建、重试一次。显式 --session 不自动重建。
    reuse_failed = reused and not explicit_session and (
        result.get("http_status") in (403, 404, 409)
        or (result.get("terminal") == "error" and _is_session_closed_reason(result.get("error")))
    )
    if reuse_failed:
        _eprint_run("复用的会话已失效，重建后重试...")
        cache = _load_run_sessions()
        cache.pop(key, None)
        _save_run_sessions(cache)
        session_id = _create_run_session(host, token, skills, timeout=min(timeout, 120))
        reused = False
        body["session_id"] = session_id
        result = _stream_run(host, token, body, json_mode=json_mode, timeout=timeout)

    if result.get("http_status") is not None:
        die(_run_status_hint(int(result["http_status"]), {"error": result.get("error")}))
    terminal = result.get("terminal")
    if terminal != "done":
        if not json_mode:
            sys.stdout.write("\n")
        if terminal in ("error", "cancelled"):
            # 后端明确回了终止帧：真正的业务错误 / 主动取消，直接透出原因。
            reason = result.get("error") or ("已取消" if terminal == "cancelled" else "未知错误")
            die(f"运行失败：{reason}")
        # terminal 为空 = 流没收到终止帧，连接被中途断开（网关空闲超时 / 网络中断）。
        # 与业务错误区分：这类任务可能仍在服务端继续，重试往往能恢复。
        msg = (
            "运行未正常结束：与服务端的流式连接被中途断开"
            "（可能是网关空闲超时或网络中断）。任务可能仍在服务端继续，"
            "可稍后重试；或加 --json 查看原始帧。"
        )
        detail = result.get("error")
        if detail:
            msg += f"（{detail}）"
        die(msg)

    # 成功 → 刷新 last_used（滑动 TTL）；显式 --session 与 --no-reuse 不写入分桶缓存。
    if not explicit_session and not no_reuse:
        cache = _load_run_sessions()
        cache[key] = {"session_id": session_id, "last_used": time.time()}
        _save_run_sessions(cache)

    if not json_mode:
        sys.stdout.write("\n")
        _eprint_run(f"完成（session={session_id}, tokens={result.get('tokens', 0)}）")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal local skills store CLI")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"skillhub {CLI_VERSION}",
        help="Show skillhub CLI version and exit",
    )
    parser.add_argument(
        "--index",
        default=DEFAULT_INDEX_URI,
        help=(
            "Skills index JSON path/URI. Supports http://, https://, file://, or local paths "
            '(default from metadata.json, e.g. "https://.../skills.json").'
        ),
    )
    parser.add_argument(
        "--dir",
        default=DEFAULT_INSTALL_ROOT,
        help='Install root directory (default: "./skills")',
    )
    parser.add_argument(
        "--skip-self-upgrade",
        action="store_true",
        help="Skip startup self-upgrade check for this run",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Search skills")
    search.add_argument("query", nargs="*", help="Search query words")
    search.add_argument(
        "--search-url",
        default=DEFAULT_SEARCH_URL,
        help=(
            "Remote search API URL (default from SKILLHUB_SEARCH_URL / metadata / built-in). "
            'Example: "http://.../api/v1/search".'
        ),
    )
    search.add_argument(
        "--search-limit",
        type=int,
        default=20,
        help="Remote search limit (default: 20)",
    )
    search.add_argument(
        "--search-timeout",
        type=int,
        default=6,
        help="Remote search timeout seconds (default: 6)",
    )
    search.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Print search results as JSON",
    )
    search.add_argument(
        "--org",
        default="",
        help="Only search specified enterprise source (org slug)",
    )
    search.set_defaults(func=cmd_search)

    # ─── skill (subcommand group) ────────────────────────────────────────────────
    skill_cmd = subparsers.add_parser("skill", help="Manage skills (e.g., skill rankings)")
    skill_subparsers = skill_cmd.add_subparsers(dest="skill_action", required=True)

    skill_rankings = skill_subparsers.add_parser("rankings", help="Fetch skill rankings as JSON")
    skill_rankings.add_argument(
        "--type",
        choices=["all", *RANKING_ENDPOINTS.keys()],
        default="all",
        help="Ranking type to fetch (default: all)",
    )
    skill_rankings.add_argument(
        "--host",
        default="",
        help=f"API host URL (default: SKILLHUB_HOST or {DEFAULT_ENTERPRISE_HOST})",
    )
    skill_rankings.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout seconds (default: 10)",
    )
    skill_rankings.set_defaults(func=cmd_rankings)

    skill_reports = skill_subparsers.add_parser(
        "reports",
        help="Fetch existing Keen and Yunding security report URLs",
    )
    skill_reports.add_argument("slug", help="Skill slug")
    skill_reports.add_argument(
        "--host",
        default="",
        help=f"API host URL (default: SKILLHUB_HOST or {DEFAULT_ENTERPRISE_HOST})",
    )
    skill_reports.add_argument(
        "--namespace",
        default="",
        help="Community namespace handle. Example: skill reports payment-sdk --namespace alice",
    )
    skill_reports.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout seconds (default: 10)",
    )
    skill_reports.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Print report result as JSON",
    )
    skill_reports.set_defaults(func=cmd_skill_reports)

    skill_evaluation = skill_subparsers.add_parser(
        "evaluation",
        help="Fetch skill evaluation report",
    )
    skill_evaluation.add_argument("slug", help="Skill slug")
    skill_evaluation.add_argument(
        "--namespace",
        default="",
        help="Community namespace handle",
    )
    skill_evaluation.add_argument(
        "--host",
        default="",
        help=f"API host URL (default: SKILLHUB_HOST or {DEFAULT_ENTERPRISE_HOST})",
    )
    skill_evaluation.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout seconds (default: 10)",
    )
    skill_evaluation.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Print evaluation result as JSON",
    )
    skill_evaluation.set_defaults(func=cmd_skill_evaluation)

    install = subparsers.add_parser("install", help="Install a skill by slug")
    install.add_argument("slug", help="Skill slug")
    install.add_argument(
        "--namespace",
        default="",
        help="Community namespace handle. Example: skillhub install payment-sdk --namespace alice",
    )
    install.add_argument(
        "--files-base-uri",
        default="",
        help=(
            "Base URI/path for local archives. Supports file://, local paths, or "
            "URL template with {slug} (examples: file://./cli/files, ./cli/files, "
            "https://example.com/files/{slug}.zip)."
        ),
    )
    install.add_argument(
        "--download-url-template",
        default=DEFAULT_SKILLS_DOWNLOAD_URL_TEMPLATE,
        help=(
            "Fallback download URL template when zip_url/local file is missing "
            '(default from metadata.json, e.g. "https://.../skills/{slug}.zip").'
        ),
    )
    install.add_argument(
        "--primary-download-url-template",
        default=DEFAULT_PRIMARY_DOWNLOAD_URL_TEMPLATE,
        help=(
            "Primary download URL template for install (supports {slug}). "
            "This is the only remote source used by install."
        ),
    )
    install.add_argument(
        "--search-url",
        default=DEFAULT_SEARCH_URL,
        help="Remote search API URL used when slug is not found in index.",
    )
    install.add_argument(
        "--search-limit",
        type=int,
        default=20,
        help="Remote search limit for install fallback (default: 20)",
    )
    install.add_argument(
        "--search-timeout",
        type=int,
        default=6,
        help="Remote search timeout for install fallback in seconds (default: 6)",
    )
    install.add_argument("--force", action="store_true", help="Overwrite existing target directory")
    install.add_argument(
        "--dir",
        default=argparse.SUPPRESS,
        help='Install root directory (default: "./skills")',
    )
    install.add_argument(
        "--secret",
        default=None,
        help=(
            "Enterprise API Key (sk-ent-...) for direct download without login. "
            "Also reads from SKILLHUB_SECRET env var. Priority: --secret > env > stored credentials."
        ),
    )
    install.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Print install result as JSON",
    )
    install.set_defaults(func=cmd_install)

    # ─── soul (subcommand group) ────────────────────────────────────────────────
    soul_cmd = subparsers.add_parser("soul", help="Manage souls (e.g., soul install <slug>)")
    soul_subparsers = soul_cmd.add_subparsers(dest="soul_action", required=True)

    soul_install = soul_subparsers.add_parser("install", help="Install a soul by slug")
    soul_install.add_argument("slug", help="Soul slug (e.g., coder-soul)")
    soul_install.add_argument("--force", action="store_true", help="Overwrite existing SOUL.md")
    soul_install.add_argument(
        "--dir",
        default=DEFAULT_INSTALL_ROOT,
        help='Install root directory (default: "./skills")',
    )
    soul_install.add_argument(
        "--output",
        default="",
        help="Output directory for SOUL.md (default: parent of install root)",
    )
    soul_install.add_argument("--json", dest="json_output", action="store_true", help="Print result as JSON")
    soul_install.set_defaults(func=cmd_install_soul)

    # ─── pack (subcommand group) ─────────────────────────────────────────────────
    pack_cmd = subparsers.add_parser("pack", help="Manage skill packs (e.g., pack install <slug>)")
    pack_subparsers = pack_cmd.add_subparsers(dest="pack_action", required=True)

    pack_install = pack_subparsers.add_parser("install", help="Install a skill pack (skillset) by slug")
    pack_install.add_argument("slug", help="SkillSet slug (e.g., gaokao-expert)")
    pack_install.add_argument("--force", action="store_true", help="Overwrite existing skills in the pack")
    pack_install.add_argument(
        "--dir",
        default=DEFAULT_INSTALL_ROOT,
        help='Install root directory (default: "./skills")',
    )
    pack_install.add_argument("--json", dest="json_output", action="store_true", help="Print result as JSON")
    pack_install.set_defaults(func=cmd_install_pack)

    upgrade = subparsers.add_parser(
        "upgrade",
        help="Upgrade installed skills based on each skill's config.json update URL",
    )
    upgrade.add_argument(
        "slug",
        nargs="?",
        default="",
        help="Optional skill slug. If omitted, upgrade all skills in lockfile.",
    )
    upgrade.add_argument(
        "--check-only",
        action="store_true",
        help="Only check and print available upgrades without installing",
    )
    upgrade.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Timeout in seconds for manifest fetch (default: 20)",
    )
    upgrade.add_argument(
        "--dir",
        default=argparse.SUPPRESS,
        help='Install root directory (default: "./skills")',
    )
    upgrade.set_defaults(func=cmd_upgrade)

    list_cmd = subparsers.add_parser("list", help="List locally installed skills")
    list_cmd.add_argument(
        "--dir",
        default=argparse.SUPPRESS,
        help='Install root directory (default: "./skills")',
    )
    list_cmd.set_defaults(func=cmd_list)

    self_upgrade = subparsers.add_parser(
        "self-upgrade",
        help="Self-upgrade this CLI from update manifest URL in config.json",
    )
    self_upgrade.add_argument(
        "--config",
        default=f"{DEFAULT_CLI_HOME}/config.json",
        help=(
            'Self-upgrade config path (default: "~/.skillhub/config.json"). '
            "If missing or no URL configured, falls back to the built-in manifest URL."
        ),
    )
    self_upgrade.add_argument(
        "--target",
        default="",
        help="CLI script target path to replace (default: current running script path)",
    )
    self_upgrade.add_argument(
        "--current-version",
        default=CLI_VERSION,
        help=f'Current CLI version for comparison (default: "{CLI_VERSION}")',
    )
    self_upgrade.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Timeout in seconds for manifest fetch/download requests (default: 20)",
    )
    self_upgrade.add_argument(
        "--check-only",
        action="store_true",
        help="Only check and print available CLI upgrade without replacing files",
    )
    self_upgrade.set_defaults(func=cmd_self_upgrade)

    # Login supports both community user tokens (skh_) and enterprise API keys.
    login_cmd = subparsers.add_parser(
        "login",
        help="Login using a community token or enterprise API key",
    )
    login_cmd.add_argument(
        "--key",
        required=True,
        help="Community token (skh_...) or enterprise API key (e.g. sk-ent-xxx)",
    )
    login_cmd.add_argument(
        "--host",
        default="",
        help=f"API host URL (default: {DEFAULT_ENTERPRISE_HOST})",
    )
    login_cmd.set_defaults(func=cmd_login)

    logout_cmd = subparsers.add_parser(
        "logout",
        help="Logout from an enterprise source",
    )
    logout_cmd.add_argument(
        "--org",
        default="",
        help="Organization slug to logout from (required if multiple orgs configured)",
    )
    logout_cmd.set_defaults(func=cmd_logout)

    config_cmd = subparsers.add_parser(
        "config",
        help="Manage CLI configuration",
    )
    config_subparsers = config_cmd.add_subparsers(dest="config_action")
    config_list_cmd = config_subparsers.add_parser(
        "list",
        help="List configured enterprise sources",
    )
    config_list_cmd.set_defaults(func=cmd_config_list)
    # config 命令默认行为也是 list
    config_cmd.set_defaults(func=cmd_config_list)

    # ============================================================
    # User API Token — auth subcommand family + publish
    # ============================================================
    auth_cmd = subparsers.add_parser(
        "auth",
        help="管理个人 API Token (skh_)",
    )
    auth_sub = auth_cmd.add_subparsers(dest="auth_action", required=True, metavar="{logout,whoami,token}")

    auth_login = auth_sub.add_parser("login", help=argparse.SUPPRESS)
    auth_login.add_argument("--token", required=True, help="个人 API Token (skh_...)")
    auth_login.add_argument(
        "--host",
        default="",
        help=f"API host (default: {DEFAULT_ENTERPRISE_HOST})",
    )
    auth_login.set_defaults(func=cmd_auth_login)
    auth_sub._choices_actions = [action for action in auth_sub._choices_actions if action.dest != "login"]

    auth_logout = auth_sub.add_parser("logout", help="清除本地保存的 API Token")
    auth_logout.set_defaults(func=cmd_auth_logout)

    auth_whoami = auth_sub.add_parser("whoami", help="查询当前 Token 对应的用户身份")
    auth_whoami.add_argument("--host", default="", help="API host (覆盖凭据中保存的 host)")
    auth_whoami.add_argument("--json", dest="json_output", action="store_true", help="JSON 输出")
    auth_whoami.set_defaults(func=cmd_auth_whoami)

    auth_token = auth_sub.add_parser("token", help="打印当前已登录 Token (CI 调试用)")
    auth_token.set_defaults(func=cmd_auth_token)

    verify_cmd = subparsers.add_parser(
        "verify",
        help="验证本机 skill 与平台签名是否一致（默认验已安装目录，或 --zip 验 zip）",
    )
    verify_cmd.add_argument("target", help="slug 或 slug@version")
    verify_cmd.add_argument("--version", default="", help="覆盖 target 中的 version")
    verify_cmd.add_argument("--namespace", default="", help="Community namespace handle")
    verify_cmd.add_argument(
        "--host",
        default="",
        help=f"API host (default: SKILLHUB_HOST or {DEFAULT_ENTERPRISE_HOST})",
    )
    verify_cmd.add_argument(
        "--zip",
        dest="zip_path",
        default="",
        help="本地 zip 路径（未指定时默认验 --dir 下已安装的 skill 目录）",
    )
    verify_cmd.add_argument("--json", dest="json_output", action="store_true", help="JSON 输出")
    verify_cmd.set_defaults(func=cmd_verify)

    publish_cmd = subparsers.add_parser("publish", help="发布 Skill 到社区源 (支持目录或 .zip)")
    publish_cmd.add_argument("path", help="本地 skill 目录路径或 .zip 文件路径，目录/zip 内必须含 SKILL.md")
    publish_cmd.add_argument("--version", default="", help="覆盖 SKILL.md 中的 version")
    publish_cmd.add_argument("--changelog", default="", help="本次发布的 changelog 文本")
    publish_cmd.add_argument("--dry-run", action="store_true", help="本地预检：仅校验 metadata + 打包，不发起 HTTP 请求")
    publish_cmd.add_argument("--token", default="", help="覆盖已登录 API Token (skh_...)")
    publish_cmd.add_argument(
        "--host",
        default="",
        help=f"API host (default: {DEFAULT_ENTERPRISE_HOST})",
    )
    publish_cmd.add_argument("--json", dest="json_output", action="store_true", help="JSON 输出")
    publish_cmd.set_defaults(func=cmd_publish)

    # ─── comment (subcommand group) ─────────────────────────────────────────────
    comment_cmd = subparsers.add_parser("comment", help="Skill 评论区（post/reply/list/replies-more/delete/like/unlike）")
    comment_sub = comment_cmd.add_subparsers(dest="comment_action", required=True)

    def _add_common_comment_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--token", default="", help="个人 API Token (skh_...)，默认用已登录凭据")
        p.add_argument("--host", default="", help=f"API host (default: {DEFAULT_ENTERPRISE_HOST})")
        p.add_argument("--namespace", default="", help="Community namespace handle")

    c_post = comment_sub.add_parser("post", help="发表一级评论")
    c_post.add_argument("slug", help="Skill slug")
    c_post.add_argument("--content", default="", help="评论内容（<=500 字；有图片时可省略）")
    c_post.add_argument("--image", action="append", metavar="PATH",
                        help="图片/表情包文件路径，可重复（jpeg/png/webp，单张<=5MB，最多 9 张）")
    c_post.add_argument("--json", dest="json_output", action="store_true", help="JSON 输出")
    _add_common_comment_args(c_post)
    c_post.set_defaults(func=cmd_comment_post)

    c_reply = comment_sub.add_parser("reply", help="对评论/回复发表回复（扁平两级，可回复回复）")
    c_reply.add_argument("slug", help="Skill slug")
    c_reply.add_argument("comment_id", type=int, metavar="commentID", help="被回复的评论/回复 id")
    c_reply.add_argument("--content", default="", help="回复内容（<=500 字；有图片时可省略）")
    c_reply.add_argument("--image", action="append", metavar="PATH",
                         help="图片/表情包文件路径，可重复（jpeg/png/webp，单张<=5MB，最多 9 张）")
    c_reply.add_argument("--json", dest="json_output", action="store_true", help="JSON 输出")
    _add_common_comment_args(c_reply)
    c_reply.set_defaults(func=cmd_comment_reply)

    c_list = comment_sub.add_parser("list", help="查看一级评论列表（含回复预览+总数），支持 --sort new|hot")
    c_list.add_argument("slug", help="Skill slug")
    c_list.add_argument("--sort", choices=["new", "hot"], default="new", help="排序：new=最新（默认），hot=热度（按点赞数）")
    c_list.add_argument("--cursor", type=int, default=0, help="游标（仅 --sort new，上一页返回的 nextCursor）")
    c_list.add_argument("--offset", type=int, default=0, help="偏移（仅 --sort hot，上限 1000）")
    c_list.add_argument("--limit", type=int, default=0, help="每页条数（默认 20，最大 100）")
    c_list.add_argument("--json", dest="json_output", action="store_true", help="JSON 输出")
    _add_common_comment_args(c_list)
    c_list.set_defaults(func=cmd_comment_list)

    c_replies = comment_sub.add_parser("replies-more", help="加载某条评论的更多回复")
    c_replies.add_argument("slug", help="Skill slug")
    c_replies.add_argument("comment_id", type=int, metavar="commentID", help="一级评论 id")
    c_replies.add_argument("--cursor", type=int, default=0, help="游标（上一页返回的 nextCursor）")
    c_replies.add_argument("--limit", type=int, default=0, help="每页条数（默认 20，最大 100）")
    c_replies.add_argument("--json", dest="json_output", action="store_true", help="JSON 输出")
    _add_common_comment_args(c_replies)
    c_replies.set_defaults(func=cmd_comment_replies_more)

    c_del = comment_sub.add_parser("delete", help="删除评论/回复（作者/owner/admin）")
    c_del.add_argument("slug", help="Skill slug")
    c_del.add_argument("comment_id", type=int, metavar="commentID", help="要删除的评论/回复 id")
    c_del.add_argument("--json", dest="json_output", action="store_true", help="JSON 输出")
    _add_common_comment_args(c_del)
    c_del.set_defaults(func=cmd_comment_delete)

    c_like = comment_sub.add_parser("like", help="点赞评论/回复（幂等，不发送站内信）")
    c_like.add_argument("slug", help="Skill slug")
    c_like.add_argument("comment_id", type=int, metavar="commentID", help="要点赞的评论/回复 id")
    c_like.add_argument("--json", dest="json_output", action="store_true", help="JSON 输出")
    _add_common_comment_args(c_like)
    c_like.set_defaults(func=cmd_comment_like)

    c_unlike = comment_sub.add_parser("unlike", help="取消点赞（幂等）")
    c_unlike.add_argument("slug", help="Skill slug")
    c_unlike.add_argument("comment_id", type=int, metavar="commentID", help="要取消点赞的评论/回复 id")
    c_unlike.add_argument("--json", dest="json_output", action="store_true", help="JSON 输出")
    _add_common_comment_args(c_unlike)
    c_unlike.set_defaults(func=cmd_comment_unlike)

    # ─── run (SSE 在线调用 skill + 会话复用) ─────────────────────────────────────
    run_cmd = subparsers.add_parser(
        "run",
        help="在线调用 skill（SSE 流式）；默认 30 分钟内同一 skills 组合复用同一会话",
    )
    run_cmd.add_argument("input", help="输入内容；传 '-' 时从 stdin 读取")
    run_cmd.add_argument(
        "--skill",
        action="append",
        metavar="SLUG",
        help=(
            "本次在线运行的 skill，可重复。仅支持服务化 skill；"
            "可传 slug（如 --skill ppt）或命名空间坐标（如 --skill @handle/ppt）。"
            "非服务化 skill 会被拒绝（403）"
        ),
    )
    run_cmd.add_argument("--session", default="", help="显式复用指定 session_id（跳过缓存/自动重建）")
    run_cmd.add_argument("--new", action="store_true", help="强制新建会话（忽略缓存）")
    run_cmd.add_argument("--no-reuse", dest="no_reuse", action="store_true", help="本次不复用也不写缓存")
    run_cmd.add_argument(
        "--ttl",
        type=int,
        default=DEFAULT_RUN_SESSION_TTL,
        help=f"会话复用滑动窗口秒数（默认 {DEFAULT_RUN_SESSION_TTL}）",
    )
    run_cmd.add_argument("--timeout", type=int, default=600, help="单次流式空闲超时秒数（默认 600）")
    run_cmd.add_argument("--json", dest="json_output", action="store_true", help="逐帧输出原始 SSE JSON")
    run_cmd.add_argument("--token", default="", help="个人 API Token (skh_...)，默认用已登录凭据")
    run_cmd.add_argument("--host", default="", help=f"API host (default: {DEFAULT_ENTERPRISE_HOST})")
    run_cmd.set_defaults(func=cmd_run)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config_path = Path(f"{DEFAULT_CLI_HOME}/{CLI_CONFIG_NAME}").expanduser().resolve()
    command = str(getattr(args, "command", "")).strip()
    # OTA check runs for all commands except explicit self-upgrade.
    # Starting from 2026.6.10, the startup path no longer silently upgrades:
    # it prompts the user in an interactive terminal and falls back to a
    # one-line hint when running non-interactively (CI, pipes, redirected IO).
    should_check_startup_upgrade = (
        command != "self-upgrade"
        and os.environ.get(SELF_UPGRADE_REEXEC_ENV, "") != "1"
        and not bool(getattr(args, "skip_self_upgrade", False))
        and should_run_startup_self_upgrade(config_path)
    )
    if should_check_startup_upgrade:
        json_output = bool(getattr(args, "json_output", False))
        upgraded = startup_self_upgrade_prompt(
            config_path=config_path,
            allow_interactive_prompt=not json_output,
        )
        if upgraded:
            env = os.environ.copy()
            env[SELF_UPGRADE_REEXEC_ENV] = "1"
            os.execve(sys.executable, [sys.executable, *sys.argv], env)
    args.func(args)


if __name__ == "__main__":
    main()
