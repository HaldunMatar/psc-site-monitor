import hashlib
import time
from datetime import datetime

from .embedder import cosine, embed
from .fetcher import FetchError, fetch_html, html_to_text
from .store import load_baseline, save_baseline


def _snapshot(url, backend, verify):
    text = html_to_text(fetch_html(url, verify=verify))
    return embed(text, backend), hashlib.sha256(text.encode()).hexdigest()


def run_baseline(url, backend, path, verify=True):
    """المرحلة 1: جلب الصفحة الرئيسية وحفظ الـ Embedding المرجعي."""
    emb, h = _snapshot(url, backend, verify)
    save_baseline(path, url, backend, emb, h)
    print(f"تم حفظ الـ Embedding المرجعي لـ {url} في {path}")


def check_once(base, url, backend, threshold, verify=True):
    """يقارن الحالة الحالية بالمرجع؛ يعيد (changed|ok|error, similarity)."""
    try:
        emb, h = _snapshot(url, backend, verify)
    except FetchError as e:
        print(f"[{datetime.now():%H:%M:%S}] تعذّر جلب الموقع (ليس تغييرًا مؤكدًا): {e}")
        return "error", None
    sim = cosine(base["embedding"], emb)
    if sim < threshold:
        print(f"[{datetime.now():%H:%M:%S}] ⚠️ يوجد تغيير / يوجد هجوم على الموقع! "
              f"(تشابه={sim:.4f} < العتبة {threshold})")
        return "changed", sim
    print(f"[{datetime.now():%H:%M:%S}] ✅ لا تغيير (تشابه={sim:.4f})")
    return "ok", sim


def run_watch(url, backend, path, threshold, interval=60, verify=True, max_checks=None):
    """المرحلة 2: فحص دوري كل `interval` ثانية."""
    base = load_baseline(path)
    if base["backend"] != backend:
        raise SystemExit(f"الـ baseline أُنشئ بـ backend={base['backend']} — استخدم نفسه.")
    n = 0
    while max_checks is None or n < max_checks:
        check_once(base, url, backend, threshold, verify)
        n += 1
        if max_checks is None or n < max_checks:
            time.sleep(interval)
