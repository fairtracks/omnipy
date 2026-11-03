"""Serve the README's example river response without contacting an external API."""

from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread

# First river sample from the water_sample_harmonization integration scenario.
RIVER_SAMPLE_PAGE = [
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
    }
]


@contextmanager
def water_sample_service() -> Iterator[str]:
    """Yield one local JSON URL; keep Omnipy's HTTP and loading code real."""
    payload = json.dumps(RIVER_SAMPLE_PAGE).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path != '/samples?page=0':
                self.send_error(404)
                return
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
            yield f'http://127.0.0.1:{server.server_port}/samples?page=0'
        finally:
            server.shutdown()
            thread.join()
