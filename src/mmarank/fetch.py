"""Download a Fight Canon release (pinned tag or latest) into data/raw/<tag>/."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

from .config import FIGHT_CANON_REPO, RAW_DIR

_UA = {"User-Agent": "mmarank (hobby project; github.com)"}


def _get_json(url: str) -> dict:
    headers = dict(_UA)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
        return json.load(r)


def latest_tag() -> str:
    return _get_json(f"https://api.github.com/repos/{FIGHT_CANON_REPO}/releases/latest")["tag_name"]


def fetch(tag: str | None = None) -> Path:
    tag = tag or latest_tag()
    dest = RAW_DIR / tag / "canon.db"
    if dest.exists():
        return dest
    rel = _get_json(f"https://api.github.com/repos/{FIGHT_CANON_REPO}/releases/tags/{tag}")
    asset = next(a for a in rel["assets"] if a["name"] == "canon.db")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(urllib.request.Request(asset["browser_download_url"], headers=_UA), timeout=600) as r, \
            open(tmp, "wb") as fh:
        while chunk := r.read(1 << 20):
            fh.write(chunk)
    if tmp.stat().st_size != asset["size"]:
        tmp.unlink()
        raise IOError(f"size mismatch for {tag}")
    tmp.rename(dest)
    return dest


def local_tags() -> list[str]:
    return sorted(p.name for p in RAW_DIR.glob("db-*") if (p / "canon.db").exists())
