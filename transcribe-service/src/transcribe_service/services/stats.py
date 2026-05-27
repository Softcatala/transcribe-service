from datetime import date

from transcribe_core.batchfilesdb import BatchFilesDB
from transcribe_core.processedfiles import ProcessedFiles
from transcribe_core.usage import Usage


class StatsService:
    """TODO: Docstring this class."""

    @staticmethod
    def get_stats(date: date) -> dict:
        """TODO: Docstring this."""
        result = Usage().get_stats(date)
        queue = {}
        records = BatchFilesDB().select()
        who = {
            record.email: sum(1 for r in records if r.email == record.email)
            for record in records
        }
        print_who = {
            "".join(["-" if c in ["a"] else c for c in key]): value
            for key, value in who.items()
        }
        result["files_stored"] = ProcessedFiles.get_num_of_files_stored()
        result["files_stored_size"] = (
            ProcessedFiles.get_num_of_files_stored_size()
        )
        result["free_storage_space"] = (
            ProcessedFiles.get_free_space_in_directory()
        )
        queue["items"] = len(records)
        queue["who"] = print_who
        result["queue"] = queue
        return result
