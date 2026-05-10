# -*- encoding: utf-8 -*-
#
# Copyright (c) 2022 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import fnmatch
import logging
import os
import shutil
import time
import uuid
from pathlib import Path

PROCESSED = "/srv/data/processed"


class ProcessedFiles:
    """TODO: Docstring this class."""

    def __init__(self, uuid: str) -> None:
        """TODO: Docstring this."""
        self.uuid = uuid

    @staticmethod
    def get_processed_directory() -> str:
        """TODO: DOcstring this."""
        return PROCESSED

    def is_valid_uuid(self) -> bool:
        """TODO: Docstring this."""
        try:
            uuid.UUID(str(self.uuid))
            return True
        except ValueError:
            return False

    def do_files_exists(self) -> tuple[bool, str]:
        """TODO: Docstring this."""
        extensions = ["txt", "srt", "dbrecord"]
        for extension in extensions:
            fullname = Path(PROCESSED) / self.uuid
            fullname = f"{fullname}.{extension}"

            if not Path(fullname).exists():
                message = f"file {extension} does not exist"
                return False, message

        return True, ""

    @staticmethod
    def ensure_dir() -> None:
        """TODO: Docstring this."""
        if not Path(PROCESSED).exists():
            Path(PROCESSED).mkdir(parents=True)

    def _get_extension(self, filename: str) -> str:
        return Path(filename).suffix

    def copy_file(self, full_filename: str) -> None:
        """TODO: Docstring this."""
        filename = Path(full_filename).name
        target = Path(PROCESSED) / filename
        shutil.copy(full_filename, target)
        logging.debug(f"Copy file {full_filename} to {target}")

    def move_file(self, full_filename: str) -> None:
        """TODO: Docstring this."""
        filename = Path(full_filename).name
        ext = self._get_extension(filename)
        target = Path(PROCESSED) / f"{self.uuid}{ext}"
        shutil.move(full_filename, target)
        logging.debug(f"Moved file {full_filename} to {target}")

    def move_file_bin(self, full_filename: str, extension: str) -> None:
        """TODO: Docstring this."""
        target = Path(PROCESSED) / f"{self.uuid}{extension}"
        shutil.move(full_filename, target)

        logging.debug(f"Moved file {full_filename} to {target}")

    def _find_files(directory: str, pattern: str) -> list[str]:
        filelist = []

        for root, _, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = str(Path(root) / basename)
                    filelist.append(filename)

        return filelist

    def get_num_of_files_stored(directory: str = PROCESSED) -> int:
        """TODO: Docstring this."""
        files = ProcessedFiles._find_files(directory, "*")
        return len(files)

    def _get_human_readable_size(size: int) -> str:
        GB_IN_BYTES = 1024**3
        if size > GB_IN_BYTES:
            gbs = size / GB_IN_BYTES
            text = f"{gbs:.2f} GB"
        else:
            text = f"{size} bytes"

        return text

    def get_num_of_files_stored_size(directory: str = PROCESSED) -> str:
        """TODO: Docstring this."""
        files = ProcessedFiles._find_files(directory, "*")
        total_size = 0
        for _file in files:
            total_size += Path(_file).stat().st_size

        return ProcessedFiles._get_human_readable_size(total_size)

    def get_free_space_in_directory(directory: str = PROCESSED) -> str:
        """TODO: Docstring this."""
        statvfs = os.statvfs(directory)

        # Available blocks * block size gives the available space in bytes
        free_space_bytes = statvfs.f_frsize * statvfs.f_bavail
        return ProcessedFiles._get_human_readable_size(free_space_bytes)

    @staticmethod
    def _delete_file(file: str) -> bool:
        try:
            Path(file).unlink()
            logging.debug(f"Deleted file: {file}")
            return True
        except Exception as e:
            logging.error(f"Error deleting file {file}: {e}")
            return False

    def purge_files(days: int, directory: str = PROCESSED) -> int:
        """TODO: Docstring this."""
        HOURS_DAY = 24
        MINUTES_HOUR = 60
        MINUTES_SEC = 60
        deleted = 0

        files = ProcessedFiles._find_files(directory, "*")
        time_limit = time.time() - (
            HOURS_DAY * MINUTES_HOUR * MINUTES_SEC * days
        )
        for file in files:
            file_time = Path(file).stat().st_mtime
            if file_time < time_limit and ProcessedFiles._delete_file(file):
                deleted += 1

        return deleted

    def delete_files(self) -> int:
        """TODO: Docstring this."""
        directory = ProcessedFiles.get_processed_directory()
        deleted = 0
        files = ProcessedFiles._find_files(directory, f"{self.uuid}.*")
        logging.info(f"Delete files: {files}")
        for file in files:
            if ProcessedFiles._delete_file(file):
                deleted += 1

        return deleted
