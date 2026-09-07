import json
from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Query, Response

from transcribe_service.services.stats import StatsService

router = APIRouter(prefix="/stats")


@router.get(path="")
def stats(
    date: Annotated[
        date | None,
        Query(title="date", description="A date in YYYY-MM-DD format"),
    ] = None,
) -> Response:
    """TODO: Docstring this endpoint."""
    if date is None:
        date = datetime.today().date()

    return Response(
        content=json.dumps(StatsService.get_stats(date), indent=4),
        media_type="application/json",
    )
