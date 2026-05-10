from enum import Enum
from uuid import UUID

from transcribe_core.processedfiles import ProcessedFiles
from transcribe_core.usage import Usage

from transcribe_service.utils import _get_record


class GetUUIDResult(Enum):  # noqa: D101
    NotValid = 1
    NotFound = 2
    Ok = 3


class DeleteUUIDResult(Enum):  # noqa: D101
    NotValid = 1
    NotFound = 2
    WrongEmail = 3
    Ok = 4


class UUIDService:
    """TODO: Docstring this class."""

    @staticmethod
    def get_uuid(uuid: UUID) -> GetUUIDResult:
        """TODO: Docstring this."""
        processed_files = ProcessedFiles(str(uuid))
        if not processed_files.is_valid_uuid():
            return GetUUIDResult.NotValid

        exists, _ = processed_files.do_files_exists()
        if not exists:
            return GetUUIDResult.NotFound
        return GetUUIDResult.Ok

    @staticmethod
    def delete_uuid(uuid: UUID, email: str) -> DeleteUUIDResult:
        """TODO: Docstring this."""

        processed_files = ProcessedFiles(str(uuid))
        if not processed_files.is_valid_uuid():
            return DeleteUUIDResult.NotValid

        exists, _ = processed_files.do_files_exists()
        if not exists:
            return DeleteUUIDResult.NotFound

        record = _get_record(str(uuid))
        if record.email != email:
            return DeleteUUIDResult.WrongEmail

        deleted = processed_files.delete_files()
        if deleted > 0:
            Usage().log("delete_transcription")
            return DeleteUUIDResult.Ok

        return DeleteUUIDResult.NotFound
