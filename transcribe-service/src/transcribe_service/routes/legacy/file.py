from typing import Annotated

from fastapi import (APIRouter, File, Form, Query, Request,
                     UploadFile)
from fastapi.responses import FileResponse, JSONResponse

from transcribe_service.constants import MAX_SIZE
from transcribe_service.services.file import (FileService, GetFileResult,
                                              UploadFileResult)

get_file_router = APIRouter(prefix="/get_file")


@get_file_router.get(path="/")
def get_file(
    uuid: Annotated[
        str | None, Query(description="The file uuid to retrieve")
    ] = None,
    ext: Annotated[
        str | None,
        Query(description="File extension for the file to retrieve"),
    ] = None,
) -> FileResponse:
    """
    Legacy endpoint for retrieving a given processed file.
    Only used temporarily to not have breaking changes.
    """
    if not ext:
        return JSONResponse(
            status_code=404,
            content={"error": "No s'ha especificat l'extensió"},
        )
    if not uuid:
        return JSONResponse(
            status_code=404,
            content={"error": "No s'ha especificat l'UUID"},
        )

    match FileService.get_file(uuid, ext):
        case GetFileResult.NotValid, _:
            return JSONResponse(
                status_code=400, content={"error": "UUID no vàlid"}
            )

        case GetFileResult.UuidNotFound, _:
            return JSONResponse(
                status_code=404, content={"error": "UUID no existeix"}
            )

        case GetFileResult.FileNotFound, _:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "No existeix aquest fitxer. Potser ja s'ha esborrat."
                },
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


upload_file_router = APIRouter(prefix="/transcribe_file")


@upload_file_router.post(path="/")
async def upload_file(
    request: Request,
    email: Annotated[str | None, Form()] = None,
    model_name: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile | None, File()] = None,
    highlight_words: Annotated[bool | None, Form()] = None,
    num_chars: Annotated[str | None, Form()] = None,
    num_sentences: Annotated[str | None, Form()] = None,
) -> dict:
    """
    Legacy endpoint to upload a file to transcribe.
    Only used temporarily to not have breaking changes.
    """

    if not file or file.filename == "":
        return JSONResponse(
            status_code=404, content={"error": "No s'ha especificat el fitxer"}
        )

    if email == "" or not email:
        return JSONResponse(
            status_code=404, content={"error": "No s'ha especificat el correu"}
        )
    if model_name == "" or not model_name:
        return JSONResponse(
            status_code=404, content={"error": "No s'ha especificat el model"}
        )

    if int(request.headers.get("content-length")) >= MAX_SIZE:
        return JSONResponse(
            status_code=413, content={"error": "El fitxer és massa gran"}
        )

    match await FileService.upload_file(
        file, email, model_name, highlight_words, num_chars, num_sentences
    ):
        case UploadFileResult.TypeNotAllowed, _:
            return JSONResponse(
                status_code=415, content={"error": "Tipus de fitxer no vàlid"}
            )

        case UploadFileResult.QueueFull, _:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Hi ha massa fitxers a la cua. Proveu-ho en una estona."
                },
            )

        case UploadFileResult.MaxPerEmailReached, _:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Ja teniu massa fitxers a la cua. Espereu-vos que es processin per enviar-ne de nous."
                },
            )

        case UploadFileResult.Ok, waiting_queue_len:
            return {"waiting_queue": str(waiting_queue_len)}
