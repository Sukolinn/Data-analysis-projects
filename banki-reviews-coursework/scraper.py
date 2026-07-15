"""
Парсер отзывов banki.ru об обслуживании юр. лиц.

Источник: https://www.banki.ru/services/responses/list/?type=business&page=N
Полный текст отзыва, оценка, банк, дата извлекаются из JSON в атрибуте
data-module-options первого модуля на странице.

Запуск:
    python scraper.py                       # с last_page из progress.json (или 1)
    python scraper.py --start-page 1 --max-pages 2000
"""

from __future__ import annotations

import argparse
import asyncio
import html as html_mod
import json
import logging
import random
import re
import signal
import sys
import time
from pathlib import Path

import httpx
import pandas as pd

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data" / "raw"
PROGRESS_FILE = ROOT / "data" / "progress.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

URL_TEMPLATE = "https://www.banki.ru/services/responses/list/?type=business&page={page}"
ATTR_RE = re.compile(r"data-module-options='([^']+)'")
TAG_RE = re.compile(r"<[^>]+>")

CONCURRENCY = 3           # параллельные запросы (снижено после rate-limit на 6)
DELAY_RANGE = (0.6, 1.4)   # джиттер между запросами в каждой корутине
BATCH_SIZE = 50            # страниц в одном parquet-файле
MAX_CONSECUTIVE_FAILS = 15
RETRY_STATUSES = {429, 403, 503, 502, 500}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.banki.ru/",
    "Cache-Control": "no-cache",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("scraper")

_stop_requested = False


def _request_stop(*_):
    global _stop_requested
    _stop_requested = True
    log.warning("Stop requested, finishing current batch...")


signal.signal(signal.SIGINT, _request_stop)
signal.signal(signal.SIGTERM, _request_stop)


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"last_completed_page": 0, "total_reviews": 0, "no_more_pages": False}


def save_progress(state: dict) -> None:
    PROGRESS_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def parse_page(html: str) -> tuple[list[dict], bool]:
    """Возвращает (reviews, has_more_pages)."""
    reviews: list[dict] = []
    has_more = False
    for raw in ATTR_RE.findall(html):
        if "dateCreate" not in raw:
            continue
        try:
            data = json.loads(html_mod.unescape(raw))
        except json.JSONDecodeError:
            continue
        responses = data.get("responses") or {}
        items = responses.get("data") or []
        has_more = bool(responses.get("hasMorePages"))
        for item in items:
            company = item.get("company") or {}
            text_html = item.get("text") or ""
            text_clean = TAG_RE.sub(" ", text_html)
            text_clean = re.sub(r"\s+", " ", text_clean).strip()
            reviews.append(
                {
                    "review_id": int(item["id"]),
                    "bank": company.get("name"),
                    "bank_code": company.get("code"),
                    "rating": int(item.get("grade")) if item.get("grade") is not None else None,
                    "date": item.get("dateCreate"),
                    "title": item.get("title"),
                    "text": text_clean,
                    "url": f"https://www.banki.ru/services/responses/bank/response/{item['id']}/",
                    "is_business": True,
                }
            )
        break
    return reviews, has_more


async def fetch_page(client: httpx.AsyncClient, page: int, sem: asyncio.Semaphore) -> tuple[int, list[dict], bool | None]:
    """Возвращает (page, reviews, has_more). has_more=None при сетевой ошибке (не интерпретировать как конец)."""
    backoff = 2.0
    for attempt in range(8):
        async with sem:
            try:
                await asyncio.sleep(random.uniform(*DELAY_RANGE))
                r = await client.get(URL_TEMPLATE.format(page=page))
                if r.status_code == 200:
                    reviews, has_more = parse_page(r.text)
                    return page, reviews, has_more
                if r.status_code in RETRY_STATUSES:
                    log.warning("page=%d status=%d attempt=%d, backing off %.1fs",
                                page, r.status_code, attempt, backoff)
                    await asyncio.sleep(backoff + random.uniform(0, 0.5))
                    backoff *= 1.8
                    continue
                log.error("page=%d unexpected status %d, giving up", page, r.status_code)
                return page, [], None
            except (httpx.RequestError, httpx.HTTPError) as e:
                log.warning("page=%d error: %r attempt=%d", page, e, attempt)
                await asyncio.sleep(backoff + random.uniform(0, 0.5))
                backoff *= 1.8
    log.error("page=%d exhausted retries", page)
    return page, [], None


def flush_batch(batch_idx: int, rows: list[dict]) -> Path:
    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["review_id"]).reset_index(drop=True)
    out = DATA_DIR / f"reviews_{batch_idx:05d}.parquet"
    df.to_parquet(out, index=False)
    return out


async def main(start_page: int, max_pages: int) -> None:
    state = load_progress()
    if start_page is None:
        start_page = state.get("last_completed_page", 0) + 1
    if state.get("no_more_pages"):
        log.info("no_more_pages flag is set in progress.json; nothing to do")
        return

    end_page = start_page + max_pages - 1
    log.info("scraping pages %d..%d", start_page, end_page)

    sem = asyncio.Semaphore(CONCURRENCY)
    timeout = httpx.Timeout(30.0, connect=10.0)
    limits = httpx.Limits(max_keepalive_connections=CONCURRENCY, max_connections=CONCURRENCY * 2)

    consecutive_fails = 0
    total_reviews_added = 0
    batch_pages = []
    batch_rows: list[dict] = []

    # batch_idx — следующий свободный номер
    existing = sorted(DATA_DIR.glob("reviews_*.parquet"))
    batch_idx = (int(existing[-1].stem.split("_")[1]) + 1) if existing else 0

    async with httpx.AsyncClient(headers=HEADERS, timeout=timeout, limits=limits,
                                  follow_redirects=True, http2=False) as client:
        page_iter = iter(range(start_page, end_page + 1))
        in_flight: set[asyncio.Task] = set()

        def schedule_next():
            try:
                p = next(page_iter)
            except StopIteration:
                return False
            task = asyncio.create_task(fetch_page(client, p, sem))
            in_flight.add(task)
            return True

        for _ in range(CONCURRENCY):
            if not schedule_next():
                break

        pages_completed_lowest_continuous = start_page - 1
        results_by_page: dict[int, tuple[list[dict], bool]] = {}
        last_has_more = True

        while in_flight and not _stop_requested:
            done, _ = await asyncio.wait(in_flight, return_when=asyncio.FIRST_COMPLETED)
            for t in done:
                in_flight.discard(t)
                page, reviews, has_more = await t
                results_by_page[page] = (reviews, has_more)
                if not reviews:
                    consecutive_fails += 1
                    if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                        log.error("too many consecutive empty pages, stopping")
                        for x in in_flight:
                            x.cancel()
                        in_flight.clear()
                        break
                else:
                    consecutive_fails = 0
                if has_more is False:
                    last_has_more = False
                schedule_next()

            # Сливаем подряд идущие готовые страницы в батч
            while (pages_completed_lowest_continuous + 1) in results_by_page:
                p = pages_completed_lowest_continuous + 1
                reviews, has_more = results_by_page.pop(p)
                batch_pages.append(p)
                batch_rows.extend(reviews)
                pages_completed_lowest_continuous = p
                total_reviews_added += len(reviews)

                if len(batch_pages) >= BATCH_SIZE:
                    out = flush_batch(batch_idx, batch_rows)
                    log.info("flushed batch #%d pages %d..%d rows=%d → %s",
                             batch_idx, batch_pages[0], batch_pages[-1], len(batch_rows), out.name)
                    batch_idx += 1
                    batch_rows = []
                    batch_pages = []
                    state["last_completed_page"] = pages_completed_lowest_continuous
                    state["total_reviews"] += total_reviews_added
                    total_reviews_added = 0
                    state["no_more_pages"] = not last_has_more
                    save_progress(state)
                    if state["no_more_pages"]:
                        log.info("no more pages, stopping")
                        for x in in_flight:
                            x.cancel()
                        in_flight.clear()
                        break

        # Финальный flush
        if batch_rows:
            out = flush_batch(batch_idx, batch_rows)
            log.info("final flush #%d pages %d..%d rows=%d → %s",
                     batch_idx, batch_pages[0], batch_pages[-1], len(batch_rows), out.name)
            state["last_completed_page"] = pages_completed_lowest_continuous
            state["total_reviews"] += total_reviews_added
            state["no_more_pages"] = not last_has_more
            save_progress(state)

    log.info("done. last_completed_page=%d total_reviews=%d no_more_pages=%s",
             state["last_completed_page"], state["total_reviews"], state["no_more_pages"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-page", type=int, default=None,
                    help="по умолчанию = last_completed_page+1 из progress.json")
    ap.add_argument("--max-pages", type=int, default=4000)
    args = ap.parse_args()

    t0 = time.time()
    asyncio.run(main(args.start_page, args.max_pages))
    log.info("elapsed: %.1f s", time.time() - t0)
