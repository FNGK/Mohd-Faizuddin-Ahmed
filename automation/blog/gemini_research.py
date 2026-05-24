"""Optional Gemini enrichment — free-tier safe: cache-first, daily caps, pause on 429."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CACHE_PATH = Path("automation/blog/data/gemini_research_cache.json")
USAGE_STATE_PATH = Path("automation/blog/data/gemini_usage_state.json")
DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_MAX_CALLS_PER_RUN = 1
DEFAULT_MAX_CALLS_PER_DAY = 2
CACHE_TTL_DAYS = 30
COOLDOWN_ON_429_HOURS = 24


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_gemini_config() -> dict[str, Any]:
    cfg: dict[str, Any] = {
        "gemini_api_key": os.getenv("GEMINI_API_KEY", "").strip(),
        "gemini_enabled": os.getenv("BLOG_GEMINI_ENABLED", "").strip() in {"1", "true", "yes"},
        "gemini_max_calls_per_run": int(
            os.getenv("BLOG_GEMINI_MAX_CALLS", str(DEFAULT_MAX_CALLS_PER_RUN))
        ),
        "gemini_max_calls_per_day": int(
            os.getenv("BLOG_GEMINI_MAX_CALLS_PER_DAY", str(DEFAULT_MAX_CALLS_PER_DAY))
        ),
        "gemini_model": os.getenv("BLOG_GEMINI_MODEL", DEFAULT_MODEL).strip(),
        "gemini_free_tier": True,
        "gemini_use_grounding": False,
        "gemini_cache_ttl_days": CACHE_TTL_DAYS,
        "gemini_cooldown_hours_on_429": COOLDOWN_ON_429_HOURS,
    }
    root = repo_root()
    for name in ("config.local.json", "config.json"):
        path = root / "automation" / "blog" / name
        if path.exists():
            file_data = json.loads(path.read_text(encoding="utf-8"))
            for key in cfg:
                if key in file_data and file_data[key] not in (None, ""):
                    cfg[key] = file_data[key]
    for int_key in ("gemini_max_calls_per_run", "gemini_max_calls_per_day", "gemini_cache_ttl_days"):
        if isinstance(cfg.get(int_key), str):
            cfg[int_key] = int(cfg[int_key])
    if isinstance(cfg.get("gemini_cooldown_hours_on_429"), str):
        cfg["gemini_cooldown_hours_on_429"] = int(cfg["gemini_cooldown_hours_on_429"])
    return cfg


def is_gemini_active(cfg: dict[str, Any] | None = None) -> bool:
    cfg = cfg or load_gemini_config()
    if not bool(cfg.get("gemini_enabled")):
        return False
    if not str(cfg.get("gemini_api_key", "")).strip():
        return False
    if _quota_paused():
        return False
    if _daily_calls_remaining(cfg) <= 0:
        return False
    return True


def usage_status(cfg: dict[str, Any] | None = None) -> str:
    """Human-readable reason when Gemini is skipped (for logs)."""
    cfg = cfg or load_gemini_config()
    if not cfg.get("gemini_enabled"):
        return "disabled in config"
    if not str(cfg.get("gemini_api_key", "")).strip():
        return "no API key"
    if _quota_paused():
        state = _load_usage_state()
        return f"quota pause until {state.get('paused_until', 'unknown')}"
    remaining = _daily_calls_remaining(cfg)
    if remaining <= 0:
        return f"daily cap reached ({cfg.get('gemini_max_calls_per_day')}/day)"
    return f"ok ({remaining} call(s) left today)"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _today_key() -> str:
    return _utc_now().strftime("%Y-%m-%d")


def _load_usage_state() -> dict[str, Any]:
    if not USAGE_STATE_PATH.exists():
        return {"daily": {}, "paused_until": None}
    return json.loads(USAGE_STATE_PATH.read_text(encoding="utf-8"))


def _save_usage_state(state: dict[str, Any]) -> None:
    USAGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    USAGE_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _quota_paused() -> bool:
    state = _load_usage_state()
    paused_until = state.get("paused_until")
    if not paused_until:
        return False
    try:
        until = datetime.fromisoformat(str(paused_until))
    except ValueError:
        return False
    if _utc_now() < until:
        return True
    state["paused_until"] = None
    _save_usage_state(state)
    return False


def _daily_calls_remaining(cfg: dict[str, Any]) -> int:
    cap = int(cfg.get("gemini_max_calls_per_day", DEFAULT_MAX_CALLS_PER_DAY))
    state = _load_usage_state()
    used_today = int(state.get("daily", {}).get(_today_key(), 0))
    return max(0, cap - used_today)


def _record_success(cfg: dict[str, Any]) -> None:
    state = _load_usage_state()
    daily = state.setdefault("daily", {})
    key = _today_key()
    daily[key] = int(daily.get(key, 0)) + 1
    state["last_success_at"] = _utc_now().isoformat()
    _save_usage_state(state)


def _record_429(cfg: dict[str, Any]) -> None:
    hours = int(cfg.get("gemini_cooldown_hours_on_429", COOLDOWN_ON_429_HOURS))
    state = _load_usage_state()
    state["paused_until"] = (_utc_now() + timedelta(hours=hours)).isoformat()
    state["last_429_at"] = _utc_now().isoformat()
    _save_usage_state(state)


def _is_quota_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "429" in text or "resource_exhausted" in text or "quota" in text


def _cache_ttl_days(cfg: dict[str, Any]) -> int:
    return int(cfg.get("gemini_cache_ttl_days", CACHE_TTL_DAYS))


def _load_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {"entries": {}}
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def _save_cache(data: dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _cache_get(slug: str, cfg: dict[str, Any]) -> dict[str, Any] | None:
    cache = _load_cache()
    entry = cache.get("entries", {}).get(slug)
    if not entry:
        return None
    try:
        saved = datetime.fromisoformat(entry["cached_at"])
    except ValueError:
        return None
    if _utc_now() - saved > timedelta(days=_cache_ttl_days(cfg)):
        return None
    return entry.get("payload")


def _cache_set(slug: str, payload: dict[str, Any]) -> None:
    cache = _load_cache()
    entries = cache.setdefault("entries", {})
    entries[slug] = {
        "cached_at": _utc_now().isoformat(),
        "payload": payload,
    }
    _save_cache(cache)


def _parse_json_response(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def _call_gemini_api(
    *,
    api_key: str,
    model: str,
    term: str,
    cluster: str,
    trend_titles: list[str],
    use_grounding: bool,
) -> dict[str, Any]:
    from google import genai
    from google.genai import types

    headlines = "\n".join(f"- {t}" for t in trend_titles[:6]) or "- (no headlines)"
    prompt = f"""SEO research assistant. Topic: {term}. Cluster: {cluster}.
Headlines (RSS only):
{headlines}

Return ONLY JSON with keys: serp_intent, funnel_stage, serp_features (array), paa_questions (array, 5 items), serp_analysis (string, max 60 words), secondary_keywords (array, 3).
Be concise. Do not claim live SERP access."""

    client = genai.Client(api_key=api_key)
    json_config = types.GenerateContentConfig(
        temperature=0.2,
        response_mime_type="application/json",
    )
    if use_grounding:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )
        except Exception as exc:
            if _is_quota_error(exc):
                raise
            use_grounding = False
        else:
            text = (response.text or "").strip()
            if text:
                return _parse_json_response(text)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=json_config,
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Empty Gemini response")
    return _parse_json_response(text)


def _merge_payload(idea: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    merged = dict(idea)
    for key in (
        "serp_intent",
        "funnel_stage",
        "serp_features",
        "paa_questions",
        "serp_analysis",
        "secondary_keywords",
    ):
        if key in payload and payload[key]:
            merged[key] = payload[key]
    merged["research_source"] = "gemini+cache"
    merged["gemini_enriched"] = True
    return merged


class GeminiBudget:
    """Per-run call cap (in addition to daily cap)."""

    def __init__(self, max_calls: int) -> None:
        self.max_calls = max(0, max_calls)
        self.used = 0

    def can_call(self) -> bool:
        return self.used < self.max_calls


def maybe_enrich_with_gemini(
    idea: dict[str, Any],
    term: str,
    trend_titles: list[str] | None,
    *,
    budget: GeminiBudget | None = None,
    force: bool = False,
) -> tuple[dict[str, Any], bool]:
    """
    Cache-first enrichment. At most one API call per run on free tier; pauses 24h after 429.
    """
    cfg = load_gemini_config()
    if not force and not is_gemini_active(cfg):
        return idea, False

    slug = str(idea.get("slug", "")).strip()
    if not slug:
        return idea, False

    cached = _cache_get(slug, cfg)
    if cached:
        return _merge_payload(idea, cached), False

    if budget and not budget.can_call():
        return idea, False
    if _daily_calls_remaining(cfg) <= 0:
        return idea, False

    api_key = str(cfg.get("gemini_api_key", "")).strip()
    model = str(cfg.get("gemini_model", DEFAULT_MODEL))
    use_grounding = bool(cfg.get("gemini_use_grounding")) and not bool(cfg.get("gemini_free_tier"))

    try:
        payload = _call_gemini_api(
            api_key=api_key,
            model=model,
            term=term,
            cluster=str(idea.get("intent_cluster", "commercial seo")),
            trend_titles=trend_titles or [],
            use_grounding=use_grounding,
        )
    except Exception as exc:
        if _is_quota_error(exc):
            _record_429(cfg)
            idea["gemini_quota_paused"] = True
        return idea, False

    _cache_set(slug, payload)
    _record_success(cfg)
    if budget:
        budget.used += 1
    return _merge_payload(idea, payload), True
