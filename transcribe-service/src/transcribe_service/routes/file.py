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
from transcribe_service.telemetry.metrics import (
    downloads_counter,
    uploaded_file_size_histogram,
    uploads_counter,
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
            status_code=400, detail="No s'ha especificat l'extensió"
        )

    match FileService.get_file(uuid, ext):
        case GetFileResult.NotValid, _:
            downloads_counter.add(
                1, {"extension": ext, "result": "invalid_uuid"}
            )
            raise HTTPException(status_code=400, detail="Uuid no vàlid")

        case GetFileResult.UuidNotFound, _:
            downloads_counter.add(
                1, {"extension": ext, "result": "uuid_not_found"}
            )
            raise HTTPException(status_code=404, detail="Uuid no existeix")

        case GetFileResult.FileNotFound, _:
            downloads_counter.add(
                1, {"extension": ext, "result": "file_not_found"}
            )
            raise HTTPException(
                status_code=404,
                detail="No existeix aquest fitxer. Potser ja s'ha esborrat",
            )

        case GetFileResult.Ok, (fullname, filenames, mimetype):
            downloads_counter.add(1, {"extension": ext, "result": "ok"})
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
    highlight_words: Annotated[bool | None, Form()] = None,
    num_chars: Annotated[str | None, Form()] = None,
    num_sentences: Annotated[str | None, Form()] = None,
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
            uploads_counter.add(
                1,
                {
                    "model": model_name,
                    "email": email,
                    "result": "file_type_not_allowed",
                },
            )
            raise HTTPException(
                status_code=415, detail="Tipus de fitxer no vàlid"
            )

        case UploadFileResult.QueueFull, _:
            uploads_counter.add(
                1,
                {"model": model_name, "email": email, "result": "queue_full"},
            )
            raise HTTPException(
                status_code=429,
                detail="Hi ha massa fitxers a la cua. Proveu-ho en una estona.",
            )

        case UploadFileResult.MaxPerEmailReached, _:
            uploads_counter.add(
                1,
                {
                    "model": model_name,
                    "email": email,
                    "result": "max_per_email_reached",
                },
            )
            raise HTTPException(
                status_code=403,
                detail="Ja teniu massa fitxers a la cua. Espereu-vos que es processin per enviar-ne de nous.",
            )

        case UploadFileResult.Ok, waiting_queue_len:
            uploads_counter.add(
                1, {"model": model_name, "email": email, "result": "ok"}
            )
            uploaded_file_size_histogram.record(
                int(request.headers.get("content-length", 0)),
                {"model": model_name, "email": email},
            )
            return {"waiting_queue": str(waiting_queue_len)}
