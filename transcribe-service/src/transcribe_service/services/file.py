import logging
from enum import Enum
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from transcribe_core.batchfilesdb import BatchFilesDB
from transcribe_core.processedfiles import ProcessedFiles

from transcribe_service.constants import (
    MAX_PER_EMAIL,
    PROCESSED_FOLDER,
    QUEUE_CAPACITY,
    UPLOAD_FOLDER,
)
from transcribe_service.utils import (
    _allowed_file,
    _get_download_names,
    _get_mimetype,
    _get_record,
)


class GetFileResult(Enum):  # noqa: D101
    NotValid = 1
    UuidNotFound = 2
    FileNotFound = 3
    Ok = 4


class UploadFileResult(Enum):  # noqa: D101
    TypeNotAllowed = 1
    QueueFull = 2
    MaxPerEmailReached = 3
    Ok = 4


class FileService:
    """TODO: Docstring this class."""

    @staticmethod
    async def upload_file(
        file: UploadFile,
        email: str,
        model_name: str,
        highlight_words: bool,  # noqa: FBT001
        num_chars: str,
        num_sentences: str,
    ) -> tuple[UploadFileResult, int | None]:
        """TODO: Docstring this."""
        if not _allowed_file(file.filename):
            return UploadFileResult.TypeNotAllowed, None

        db = BatchFilesDB()
        if db.count() >= QUEUE_CAPACITY:
            logging.info(
                f"POST /file/transcribe - masses fitxers a la cua - {email}"
            )
            return UploadFileResult.QueueFull, None

        if len(db.select(email=email)) >= MAX_PER_EMAIL:
            logging.info(
                f"POST /file/transcribe - masses fitxers per email - {email}"
            )
            return UploadFileResult.MaxPerEmailReached, None

        waiting_queue = len(db.select())
        _uuid = db.get_new_uuid()
        fullname = Path(UPLOAD_FOLDER) / _uuid
        contents = await file.read()
        fullname.write_bytes(contents)
        db.create(
            fullname,
            email=email,
            model_name=model_name,
            original_filename=file.filename,
            highlight_words=highlight_words,
            num_chars=num_chars,
            num_sentences=num_sentences,
            record_uuid=_uuid,
        )

        size_mb = fullname.stat().st_size / 1024 / 1024
        logging.info(
            f"Saved file {file.filename} to {fullname} (size: {size_mb:.2f}MB) for user {email}, waiting_queue: {waiting_queue}"
        )
        return UploadFileResult.Ok, waiting_queue

    @staticmethod
    def get_file(
        uuid: UUID, ext: str
    ) -> tuple[GetFileResult, tuple[str, str, str] | None]:
        """TODO: Docstring this"""
        processed_files = ProcessedFiles(str(uuid))
        if not processed_files.is_valid_uuid():
            logging.debug(f"GET /file/{uuid} - uuid no vàlid")
            return GetFileResult.NotValid, None

        exists, _ = processed_files.do_files_exists()
        if not exists:
            logging.debug(f"GET /file/{uuid} - uuid no existeix")
            return GetFileResult.UuidNotFound, None

        record = _get_record(str(uuid))
        original_name = Path(record.original_filename).stem
        original_ext = Path(record.original_filename).suffix

        if ext == "bin":
            ext = original_ext[1:]

        fullname = Path(PROCESSED_FOLDER) / str(uuid)
        fullname = f"{fullname}.{ext}"

        if not Path(fullname).exists():
            return GetFileResult.FileNotFound, None

        filenames = _get_download_names(original_name, ext)
        mime_type = _get_mimetype(ext)
        return GetFileResult.Ok, (fullname, filenames, mime_type)
