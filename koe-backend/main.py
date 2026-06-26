from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import translate, tts, analytics
from config import BACKEND_PORT

app = FastAPI(
    title="Koe API",
    description="AI-powered sign language translation backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(translate.router, prefix="/translate", tags=["translate"])
app.include_router(tts.router, prefix="/tts", tags=["tts"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "koe-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=BACKEND_PORT, reload=True)
