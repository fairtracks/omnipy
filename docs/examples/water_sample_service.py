"""Serve the README's example river responses without contacting an external API."""

from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from urllib.parse import parse_qs, urlparse

# The river pages from the water_sample_harmonization integration scenario.
RIVER_SAMPLE_PAGES = {
    0: [
        {
            'river_sample_id': 'river-sample-1',
            'catchment': 'glomma-upper',
            'sampled_at': '2026-05-03',
            'station': 'River Mouth',
            'sample_alias': 'River-R1',
            'measurements': [
                {'name': 'Nitrate', 'value_mg_l': 1.2},
                {'name': 'Phosphorus', 'value_ug_l': 120.0},
            ],
        },
        {
            'river_sample_id': 'river-sample-2',
            'catchment': 'glomma-upper',
            'sampled_at': '2026-05-10',
            'station': 'River Mouth',
            'sample_alias': 'River-R2',
            'measurements': [
                {'name': 'nitrate', 'value_mg_l': 1.4},
            ],
        },
    ],
    1: [
        {
            'river_sample_id': 'river-sample-3',
            'catchment': 'glomma-upper',
            'sampled_at': '2026-05-17',
            'station': 'Upstream Bend',
            'sample_alias': 'River-R3',
            'measurements': [
                {'name': 'Temperature', 'value_celsius': 9.8},
            ],
        },
    ],
}


@contextmanager
def water_sample_service() -> Iterator[str]:
    """Yield a local base URL serving `/samples?page=N`; keep Omnipy's loading code real."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            url = urlparse(self.path)
            page = int(parse_qs(url.query).get('page', ['-1'])[0])
            if url.path != '/samples' or page not in RIVER_SAMPLE_PAGES:
                self.send_error(404)
                return
            payload = json.dumps(RIVER_SAMPLE_PAGES[page]).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            pass

    with ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f'http://127.0.0.1:{server.server_port}'
        finally:
            server.shutdown()
            thread.join()
