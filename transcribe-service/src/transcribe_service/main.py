from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from transcribe_service.logging import init_logging
from transcribe_service.routes import file, stats, uuid


@asynccontextmanager
async def lifespan(_app: FastAPI):  # noqa: ANN201, D103
    init_logging()
    yield


app = FastAPI(title="Softcatalà Transcription Service", lifespan=lifespan)

app.include_router(stats.router)
app.include_router(uuid.router)
app.include_router(file.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8700)
