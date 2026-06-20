from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response

from transcribe_service.services.uuid import (DeleteUUIDResult, GetUUIDResult,
                                              UUIDService)

get_uuid_router = APIRouter(prefix="/uuid_exists")


@get_uuid_router.get(path="/")
def get_uuid(
    uuid: Annotated[UUID, Query(description="UUID to check if exists")],
) -> None:
    """
    Legacy check if UUID exists endpoint.
    Only used temporarily to not have breaking changes.
    """
    match UUIDService.get_uuid(uuid):
        case GetUUIDResult.NotValid:
            raise HTTPException(status_code=422, detail="UUID no vàlid")

        case GetUUIDResult.NotFound:
            raise HTTPException(
                status_code=404, detail=f"No existeix el fitxer {uuid}"
            )

        case GetUUIDResult.Ok:
            return Response(status_code=200)


delete_uuid_router = APIRouter(prefix="/delete_uuid")


@delete_uuid_router.post(path="/")
def delete_uuid(
    uuid: Annotated[UUID, Query(description="UUID to delete")],
    email: Annotated[
        str | None, Query(description="Email of the user who created the file")
    ] = None,
):
    """
    Legacy endpoint to delete a file UUID.
    Only used temporarily to not have breaking changes.
    """
    if not email:
        raise HTTPException(
            status_code=422, detail="No s'ha especificat el correu"
        )

    match UUIDService.delete_uuid(uuid, email):
        case DeleteUUIDResult.NotValid:
            raise HTTPException(status_code=400, detail="UUID no vàlid")

        case DeleteUUIDResult.NotFound:
            raise HTTPException(
                status_code=404,
                detail="No s'ha trobat la transcripció a borrar",
            )

        case DeleteUUIDResult.WrongEmail:
            raise HTTPException(
                status_code=400,
                detail="El correu electrònic no coincideix amb el que ens vau donar.",
            )

        case DeleteUUIDResult.Ok:
            return Response(status_code=204)
