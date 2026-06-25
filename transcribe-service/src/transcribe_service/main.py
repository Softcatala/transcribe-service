from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from transcribe_service.logging import init_logging
from transcribe_service.routes import file, stats, uuid
from transcribe_service.routes.legacy import file as legacy_file
from transcribe_service.routes.legacy import uuid as legacy_uuid


@asynccontextmanager
async def lifespan(_app: FastAPI):  # noqa: ANN201, D103
    init_logging()
    yield


app = FastAPI(title="Softcatalà Transcription Service", lifespan=lifespan)

app.include_router(stats.router)
app.include_router(uuid.router)
app.include_router(file.router)
app.include_router(legacy_uuid.get_uuid_router)
app.include_router(legacy_uuid.delete_uuid_router)
app.include_router(legacy_file.get_file_router)
app.include_router(legacy_file.upload_file_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8700)
