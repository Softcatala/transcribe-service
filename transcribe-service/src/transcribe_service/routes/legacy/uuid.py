from typing import Annotated

from fastapi import APIRouter, Form, Query, Response
from fastapi.responses import JSONResponse

from transcribe_service.services.uuid import (
    DeleteUUIDResult,
    GetUUIDResult,
    UUIDService,
)
from transcribe_service.telemetry.metrics import deleted_counter

get_uuid_router = APIRouter(prefix="/uuid_exists")


@get_uuid_router.get(path="/")
def get_uuid(
    uuid: Annotated[
        str | None, Query(description="UUID to check if exists")
    ] = None,
) -> None:
    """
    Legacy check if UUID exists endpoint.
    Only used temporarily to not have breaking changes.
    """
    if not uuid:
        return JSONResponse(
            content={"error": "No s'ha especificat l'uuid"}, status_code=404
        )

    match UUIDService.get_uuid(uuid):
        case GetUUIDResult.NotValid:
            return JSONResponse(
                content={"error": "UUID no vàlid"}, status_code=400
            )

        case GetUUIDResult.NotFound:
            return JSONResponse(
                status_code=404,
                content={"error": f"No existeix el fitxer {uuid}"},
            )

        case GetUUIDResult.Ok:
            return Response(status_code=200)


delete_uuid_router = APIRouter(prefix="/delete_uuid")


@delete_uuid_router.post(path="/")
def delete_uuid(
    uuid: Annotated[str | None, Form()] = None,
    email: Annotated[str | None, Form()] = None,
):
    """
    Legacy endpoint to delete a file UUID.
    Only used temporarily to not have breaking changes.
    """
    if not email:
        return JSONResponse(
            status_code=404, content={"error": "No s'ha especificat el correu"}
        )

    if not uuid:
        return JSONResponse(
            status_code=400, content={"error": "UUID no vàlid"}
        )

    match UUIDService.delete_uuid(uuid, email):
        case DeleteUUIDResult.NotValid:
            deleted_counter.add(1, {"result": "uuid_not_valid"})
            return JSONResponse(
                status_code=400, content={"error": "UUID no vàlid"}
            )

        case DeleteUUIDResult.NotFound:
            deleted_counter.add(1, {"result": "uuid_not_found"})
            return JSONResponse(
                status_code=404,
                content={"error": "No s'ha trobat la transcripció a esborrar"},
            )

        case DeleteUUIDResult.WrongEmail:
            deleted_counter.add(1, {"result": "wrong_email"})
            return JSONResponse(
                status_code=400,
                content={
                    "error": "El correu electrònic no coincideix amb el que ens vau donar."
                },
            )

        case DeleteUUIDResult.Ok:
            deleted_counter.add(1, {"result": "ok"})
            return JSONResponse(status_code=200, content={})
