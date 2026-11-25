import tempfile
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from transcribe_service.routes import file
from transcribe_service.routes.legacy import file as legacy_file
from transcribe_service.services.file import GetFileResult
from transcribe_service.utils import _get_content_disposition

UUID = "6f1c7a52-3d1e-4b8a-9f0e-2a4b5c6d7e8f"
NAME = "Reel de SC (Reel d'Instagram)"
EXPECTED = (
    "attachment; filename=\"Reel de SC (Reel d'Instagram).srt\"; "
    "filename*=UTF-8''Reel%20de%20SC%20%28Reel%20d%27Instagram%29.srt"
)


class TestGetFile(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(file.router)
        app.include_router(legacy_file.get_file_router)
        self.client = TestClient(app)

        tmp = tempfile.NamedTemporaryFile(suffix=".srt", delete=False)
        tmp.write(b"1\n00:00:00,000 --> 00:00:01,000\nHola\n")
        tmp.close()
        result = (
            GetFileResult.Ok,
            (tmp.name, _get_content_disposition(NAME, "srt"), "text/plain"),
        )
        patcher = patch(
            "transcribe_service.services.file.FileService.get_file",
            return_value=result,
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_content_disposition(self):
        self.assertEqual(EXPECTED, _get_content_disposition(NAME, "srt"))

    def test_ascii_fallback_strips_quotes(self):
        self.assertTrue(
            _get_content_disposition('a"b\\c', "txt").startswith(
                'attachment; filename="a_b_c.txt";'
            )
        )

    def test_legacy_endpoint_sends_header_once(self):
        response = self.client.get(f"/get_file/?uuid={UUID}&ext=srt")
        self.assertEqual(200, response.status_code)
        self.assertEqual(EXPECTED, response.headers["content-disposition"])

    def test_file_endpoint_sends_header_once(self):
        response = self.client.get(f"/file/{UUID}?ext=srt")
        self.assertEqual(200, response.status_code)
        self.assertEqual(EXPECTED, response.headers["content-disposition"])


if __name__ == "__main__":
    unittest.main()
