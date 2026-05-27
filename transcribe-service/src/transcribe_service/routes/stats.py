from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Query

from transcribe_service.services.stats import StatsService

router = APIRouter(prefix="/stats")


@router.get(path="/")
def stats(
    date: Annotated[
        date | None,
        Query(title="date", description="A date in YYYY-MM-DD format"),
    ],
) -> dict:
    """TODO: Docstring this endpoint."""
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")

    return StatsService.get_stats(date)
