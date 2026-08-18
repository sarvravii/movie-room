from fastapi import FastAPI

from app.routers import movies, rooms, ws

app = FastAPI(title="Movie Room API")
app.include_router(rooms.router)
app.include_router(movies.router)
app.include_router(ws.router)


@app.get("/health")
def health():
    return {"status": "ok"}
