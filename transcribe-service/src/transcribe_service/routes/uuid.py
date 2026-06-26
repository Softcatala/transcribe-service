from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response

from transcribe_service.services.uuid import (
    DeleteUUIDResult,
    GetUUIDResult,
    UUIDService,
)
from transcribe_service.telemetry.metrics import deleted_counter

router = APIRouter(prefix="/uuid")


@router.get(path="/{uuid}")
def get_uuid(uuid: UUID) -> None:
    """TODO: Docstring this endpoint."""
    match UUIDService.get_uuid(uuid):
        case GetUUIDResult.NotValid:
            raise HTTPException(status_code=400, detail="UUID no vàlid")

        case GetUUIDResult.NotFound:
            raise HTTPException(
                status_code=404, detail=f"No existeix el fitxer {uuid}"
            )

        case GetUUIDResult.Ok:
            return Response(status_code=200)


@router.delete(path="/{uuid}")
def delete_uuid(
    uuid: UUID,
    email: Annotated[
        str | None, Query(description="Email of the user who created the file")
    ] = None,
) -> None:
    """TODO: Docstring this."""

    if not email:
        raise HTTPException(
            status_code=400, detail="No s'ha especificat el correu"
        )

    match UUIDService.delete_uuid(uuid, email):
        case DeleteUUIDResult.NotValid:
            deleted_counter.add(1, {"uuid": uuid, "result": "uuid_not_valid"})
            raise HTTPException(status_code=400, detail="UUID no vàlid")

        case DeleteUUIDResult.NotFound:
            deleted_counter.add(1, {"uuid": uuid, "result": "uuid_not_found"})
            raise HTTPException(
                status_code=404,
                detail="No s'ha trobat la transcripció a borrar",
            )

        case DeleteUUIDResult.WrongEmail:
            deleted_counter.add(1, {"uuid": uuid, "result": "wrong_email"})
            raise HTTPException(
                status_code=400,
                detail="El correu electrònic no coincideix amb el que ens vau donar.",
            )

        case DeleteUUIDResult.Ok:
            deleted_counter.add(1, {"uuid": uuid, "result": "ok"})
            return Response(status_code=204)
