from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.responses import FileResponse

from transcribe_service.constants import MAX_SIZE
from transcribe_service.services.file import (
    FileService,
    GetFileResult,
    UploadFileResult,
)

router = APIRouter(prefix="/file")


@router.get(path="/{uuid}")
def get_file(
    uuid: UUID,
    ext: Annotated[
        str | None,
        Query(description="File extension for the file to retrieve"),
    ] = None,
) -> FileResponse:
    """TODO: Docstring this."""
    if not ext:
        raise HTTPException(
            status_code=422, detail="No s'ha especificat l'extensió"
        )

    match FileService.get_file(uuid, ext):
        case GetFileResult.NotValid, _:
            raise HTTPException(status_code=422, detail="Uuid no vàlid")

        case GetFileResult.UuidNotFound, _:
            raise HTTPException(status_code=422, detail="Uuid no existeix")

        case GetFileResult.FileNotFound, _:
            raise HTTPException(
                status_code=422,
                detail="No existeix aquest fitxer. Potser ja s'ha esborrat",
            )

        case GetFileResult.Ok, (fullname, filenames, mimetype):
            return FileResponse(
                path=fullname,
                media_type=mimetype,
                filename=filenames,
                headers={
                    "Accept-Ranges": "bytes",
                    "Access-Control-Expose-Headers": "Content-Disposition",
                },
            )


@router.post(path="/transcribe")
async def upload_file(
    request: Request,
    file: Annotated[UploadFile, File()],
    email: Annotated[str, Form()],
    model_name: Annotated[str, Form()],
    highlight_words: Annotated[bool, Form()],
    num_chars: Annotated[str, Form()],
    num_sentences: Annotated[str, Form()],
) -> dict:
    """TODO: Docstring this endpoint."""
    if (
        email == ""
        or model_name == ""
        or num_chars == ""
        or num_sentences == ""
    ):
        raise HTTPException(
            status_code=400, detail="Form fields cannot be empty"
        )

    if int(request.headers.get("content-length")) >= MAX_SIZE:
        raise HTTPException(status_code=413, detail="El fitxer és massa gran")

    match await FileService.upload_file(
        file, email, model_name, highlight_words, num_chars, num_sentences
    ):
        case UploadFileResult.TypeNotAllowed, _:
            raise HTTPException(
                status_code=415, detail="Tipus de fitxer no vàlid"
            )

        case UploadFileResult.QueueFull, _:
            raise HTTPException(
                status_code=429,
                detail="Hi ha massa fitxers a la cua. Proveu-ho en una estona.",
            )

        case UploadFileResult.MaxPerEmailReached, _:
            raise HTTPException(
                status_code=403,
                detail="Ja teniu massa fitxers a la cua. Espereu-vos que es processin per enviar-ne de nous.",
            )

        case UploadFileResult.Ok, waiting_queue_len:
            return {"waiting_queue": str(waiting_queue_len)}
