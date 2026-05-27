import uvicorn
from fastapi import FastAPI

from transcribe_service.routes import stats

app = FastAPI(title="Softcatalà Transcription Service")

app.include_router(stats.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8700)
