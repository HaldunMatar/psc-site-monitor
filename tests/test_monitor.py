import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from psc_monitor.core import check_once, run_baseline
from psc_monitor.embedder import cosine, embed
from psc_monitor.fetcher import FetchError, fetch_html, html_to_text
from psc_monitor.store import load_baseline

PAGE = ("<html><body><script>x=1</script><h1>الهيئة العامة</h1>"
        + "<p>أخبار الهيئة وخدماتها للمواطنين</p>" * 30 + "</body></html>")
HACKED = "<html><body><h1>Hacked by someone</h1><p>defaced</p></body></html>"


@pytest.fixture
def server():
    state = {"html": PAGE}

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(state["html"].encode())

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}", state
    srv.shutdown()


def test_html_to_text_strips_scripts():
    assert "x=1" not in html_to_text(PAGE)
    assert "الهيئة العامة" in html_to_text(PAGE)


def test_embedding_deterministic_and_discriminative():
    a, b = embed(html_to_text(PAGE)), embed(html_to_text(PAGE))
    assert cosine(a, b) == pytest.approx(1.0)
    assert cosine(a, embed(html_to_text(HACKED))) < 0.5


def test_fetch_error():
    with pytest.raises(FetchError):
        fetch_html("http://127.0.0.1:1", timeout=2)


def test_no_change_then_change(server, tmp_path, capsys):
    url, state = server
    path = tmp_path / "b.json"
    run_baseline(url, "hash", path)
    base = load_baseline(path)
    assert check_once(base, url, "hash", 0.98)[0] == "ok"
    state["html"] = HACKED
    status, sim = check_once(base, url, "hash", 0.98)
    assert status == "changed" and sim < 0.98
    assert "يوجد تغيير" in capsys.readouterr().out


def test_fetch_failure_is_not_reported_as_attack(tmp_path, server):
    url, _ = server
    path = tmp_path / "b.json"
    run_baseline(url, "hash", path)
    base = load_baseline(path)
    assert check_once(base, "http://127.0.0.1:1", "hash", 0.98)[0] == "error"
