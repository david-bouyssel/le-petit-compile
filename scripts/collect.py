#!/usr/bin/env python3
"""Collecte les articles récents des flux RSS/Atom et de la une de Hacker News.

Sortie : work/candidates.json, la liste des candidats que l'agent trie et résume.
Bibliothèque standard uniquement, pour tourner sans installation dans le cloud.

Usage : python scripts/collect.py [--hours N]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "sources.json"
EDITIONS = ROOT / "data" / "editions"
OUT = ROOT / "work" / "candidates.json"

USER_AGENT = "Mozilla/5.0 (compatible; le-petit-compile/1.0; +https://github.com/)"
TIMEOUT = 20
EXCERPT_MAX = 700
TRACKING = re.compile(r"^(utm_|fbclid$|gclid$|mc_|ref$|ref_src$|xtor$)")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


def normalize_url(url: str) -> str:
    """Clé de déduplication : sans fragment, paramètres de suivi ni slash final."""
    try:
        p = urllib.parse.urlsplit(url.strip())
    except ValueError:
        return url.strip()
    query = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not TRACKING.match(k)]
    host = p.netloc.lower().removeprefix("www.")
    path = p.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit(("https", host, path, urllib.parse.urlencode(query), ""))


def clean_text(raw: str | None) -> str:
    if not raw:
        return ""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:EXCERPT_MAX] + ("…" if len(text) > EXCERPT_MAX else "")


def parse_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    raw = raw.strip()
    try:
        dt = parsedate_to_datetime(raw)
    except (TypeError, ValueError, IndexError):
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def child_text(el: ET.Element, *names: str) -> str | None:
    for c in el:
        if local(c.tag) in names and (c.text or "").strip():
            return c.text
    return None


def atom_link(el: ET.Element) -> str | None:
    best = None
    for c in el:
        if local(c.tag) != "link":
            continue
        href = c.get("href")
        if href and c.get("rel", "alternate") == "alternate":
            return href
        best = best or href or (c.text or "").strip() or None
    return best


def parse_feed(data: bytes) -> list[dict]:
    root = ET.fromstring(data)
    entries = [el for el in root.iter() if local(el.tag) in ("item", "entry")]
    items = []
    for el in entries:
        title = clean_text(child_text(el, "title"))
        link = atom_link(el)
        if not link:
            continue
        summary = child_text(el, "description", "summary", "encoded", "content")
        date = parse_date(child_text(el, "pubdate", "published", "updated", "date"))
        items.append({"titre": title, "url": link.strip(), "date": date, "extrait": clean_text(summary)})
    return items


def load_seen(days: int = 30) -> set[str]:
    """URL déjà publiées dans les éditions récentes, pour ne pas les reproposer."""
    seen: set[str] = set()
    if not EDITIONS.exists():
        return seen
    for path in sorted(EDITIONS.glob("*.json"))[-days:]:
        try:
            ed = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for item in [ed.get("une") or {}] + list(ed.get("items") or []):
            if item.get("url"):
                seen.add(normalize_url(item["url"]))
    return seen


def collect_feed(rubrique: str, feed: dict, since: datetime, max_items: int) -> tuple[dict, list[dict]]:
    status = {"rubrique": rubrique, "name": feed["name"], "url": feed["url"], "ok": False, "count": 0, "error": None}
    try:
        items = parse_feed(fetch(feed["url"]))
    except Exception as exc:  # flux mort, réseau bloqué, XML invalide
        status["error"] = f"{type(exc).__name__}: {exc}"[:200]
        return status, []
    recent = [i for i in items if i["date"] is None or i["date"] >= since]
    recent.sort(key=lambda i: i["date"] or since, reverse=True)
    recent = recent[:max_items]
    for i in recent:
        i["rubrique_suggeree"] = rubrique
        i["source"] = feed["name"]
    status.update(ok=True, count=len(recent))
    return status, recent


def collect_hn(url: str) -> tuple[dict, list[dict]]:
    status = {"rubrique": None, "name": "Hacker News (une)", "url": url, "ok": False, "count": 0, "error": None}
    try:
        hits = json.loads(fetch(url)).get("hits", [])
    except Exception as exc:
        status["error"] = f"{type(exc).__name__}: {exc}"[:200]
        return status, []
    stories = []
    for h in hits:
        hn_url = f"https://news.ycombinator.com/item?id={h.get('objectID')}"
        stories.append({
            "titre": h.get("title") or "",
            "url": h.get("url") or hn_url,
            "date": parse_date(h.get("created_at")),
            "extrait": clean_text(h.get("story_text")),
            "source": "Hacker News",
            "rubrique_suggeree": None,
            "hn": {"url": hn_url, "points": h.get("points") or 0, "comments": h.get("num_comments") or 0},
        })
    status.update(ok=True, count=len(stories))
    return status, stories


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=cfg.get("window_hours", 30))
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=args.hours)
    max_items = cfg.get("max_per_feed", 15)

    jobs = [(r["id"], f) for r in cfg["rubriques"] for f in r["feeds"]]
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(lambda j: collect_feed(j[0], j[1], since, max_items), jobs))
        hn_future = pool.submit(collect_hn, cfg["hacker_news"]["front_page"])
        hn_status, hn_stories = hn_future.result()

    statuses = [s for s, _ in results] + [hn_status]
    seen = load_seen()
    hn_by_url = {normalize_url(s["url"]): s for s in hn_stories}

    candidates: dict[str, dict] = {}
    for _, items in results:
        for item in items:
            key = normalize_url(item["url"])
            if key in seen or key in candidates:
                continue
            hn = hn_by_url.get(key)
            item["hn"] = hn["hn"] if hn else None
            candidates[key] = item
    for key, story in hn_by_url.items():
        if key not in seen and key not in candidates:
            candidates[key] = story

    out = []
    for n, item in enumerate(sorted(candidates.values(), key=lambda i: i["date"] or since, reverse=True), 1):
        item["id"] = f"c{n:03d}"
        item["date"] = item["date"].isoformat() if item["date"] else None
        out.append({k: item[k] for k in ("id", "rubrique_suggeree", "source", "titre", "url", "date", "extrait", "hn")})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "collecte": now.isoformat(timespec="seconds"),
        "fenetre_heures": args.hours,
        "deja_publies_ignores": len(seen),
        "flux": statuses,
        "candidats": out,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    ok = sum(1 for s in statuses if s["ok"])
    print(f"{len(out)} candidats depuis {ok}/{len(statuses)} sources -> {OUT.relative_to(ROOT)}")
    for s in statuses:
        if not s["ok"]:
            print(f"  ECHEC {s['name']}: {s['error']}")
    by_rub: dict[str, int] = {}
    for c in out:
        by_rub[c["rubrique_suggeree"] or "hn"] = by_rub.get(c["rubrique_suggeree"] or "hn", 0) + 1
    print("  par rubrique : " + ", ".join(f"{k}={v}" for k, v in sorted(by_rub.items())))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
