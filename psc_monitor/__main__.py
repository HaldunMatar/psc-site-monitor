import argparse

from .core import run_baseline, run_watch
from .fetcher import FetchError
from .store import DEFAULT_PATH


def main():
    p = argparse.ArgumentParser(prog="psc_monitor")
    p.add_argument("command", choices=["baseline", "watch"],
                   help="baseline = المرحلة 1، watch = المرحلة 2")
    p.add_argument("url", help="رابط الموقع المراد مراقبته")
    p.add_argument("--backend", choices=["hash", "sbert"], default="hash")
    p.add_argument("--baseline-file", default=str(DEFAULT_PATH))
    p.add_argument("--threshold", type=float, default=0.98,
                   help="أقل تشابه (cosine) مسموح قبل اعتباره تغييرًا")
    p.add_argument("--interval", type=int, default=60, help="ثواني بين كل فحص")
    p.add_argument("--insecure", action="store_true", help="تجاهل التحقق من شهادة TLS")
    a = p.parse_args()
    verify = not a.insecure
    try:
        if a.command == "baseline":
            run_baseline(a.url, a.backend, a.baseline_file, verify)
        else:
            run_watch(a.url, a.backend, a.baseline_file, a.threshold, a.interval, verify)
    except FetchError as e:
        raise SystemExit(f"تعذّر جلب الموقع: {e}")
    except FileNotFoundError as e:
        raise SystemExit(str(e))
    except KeyboardInterrupt:
        print("\nتم الإيقاف.")


main()
