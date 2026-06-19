import sys
import unittest
from http.client import RemoteDisconnected
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from amd_insider_monitor import http_get, http_post_json


class TimeoutResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        raise TimeoutError("read timed out")


class SuccessResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return b"ok"


class HttpRetryTests(unittest.TestCase):
    def test_http_get_retries_socket_read_timeout(self) -> None:
        responses = [TimeoutResponse(), SuccessResponse()]

        with patch("urllib.request.urlopen", side_effect=responses) as urlopen, patch("time.sleep"):
            body = http_get("https://data.sec.gov/test.json", "tester contact@example.com", retries=1)

        self.assertEqual(body, b"ok")
        self.assertEqual(urlopen.call_count, 2)

    def test_http_get_retries_remote_disconnect(self) -> None:
        responses = [RemoteDisconnected("Remote end closed connection without response"), SuccessResponse()]

        with patch("urllib.request.urlopen", side_effect=responses) as urlopen, patch("time.sleep"):
            body = http_get("https://www.sec.gov/form4.xml", "tester contact@example.com", retries=1)

        self.assertEqual(body, b"ok")
        self.assertEqual(urlopen.call_count, 2)

    def test_http_post_json_retries_socket_read_timeout(self) -> None:
        responses = [TimeoutResponse(), SuccessResponse()]

        with patch("urllib.request.urlopen", side_effect=responses) as urlopen, patch("time.sleep"):
            body = http_post_json("https://example.supabase.co/rest/v1/table", [{"id": 1}], {}, retries=1)

        self.assertEqual(body, b"ok")
        self.assertEqual(urlopen.call_count, 2)

    def test_http_post_json_retries_remote_disconnect(self) -> None:
        responses = [RemoteDisconnected("Remote end closed connection without response"), SuccessResponse()]

        with patch("urllib.request.urlopen", side_effect=responses) as urlopen, patch("time.sleep"):
            body = http_post_json("https://example.supabase.co/rest/v1/table", [{"id": 1}], {}, retries=1)

        self.assertEqual(body, b"ok")
        self.assertEqual(urlopen.call_count, 2)


if __name__ == "__main__":
    unittest.main()
