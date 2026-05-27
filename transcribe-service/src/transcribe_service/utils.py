import unicodedata
from urllib.parse import quote

from transcribe_core.batchfilesdb import BatchFile, BatchFilesDB
from transcribe_core.processedfiles import ProcessedFiles

from transcribe_service.constants import ALLOWED_MIMEYPES


def _get_record(_uuid: str) -> BatchFile | None:
    processed_dir = ProcessedFiles.get_processed_directory()
    db = BatchFilesDB(processed_dir)
    return db._read_record_from_uuid(_uuid)


# Reference: https://github.com/pallets/werkzeug/blob/main/src/werkzeug/utils.py#L454
def _get_download_names(download_name: str, ext: str) -> str:
    simple = unicodedata.normalize("NFKD", download_name)
    simple = simple.encode("ascii", "ignore").decode("ascii")
    # safe = RFC 5987 attr-char
    quoted = quote(download_name, safe="!#$&+-.^_`|~")
    names = f"filename=\"{simple}.{ext}\"; filename*=UTF-8''{quoted}.{ext}"
    return names


def _get_mimetype(extension: str) -> str:
    mimetype = ALLOWED_MIMEYPES.get(extension)

    if not mimetype:
        if extension == "txt":
            mimetype = "text/plain"
        elif extension == "json":
            mimetype = "application/json"
        else:
            mimetype = "application/octet-stream"

    return mimetype


def _allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_MIMEYPES
    )
