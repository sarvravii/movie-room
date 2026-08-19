from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import movies, rooms, ws

app = FastAPI(title="Movie Room API")

# TODO: tighten allow_origins to the real Vercel domain once it's assigned.
# Wildcard is a temporary placeholder so the frontend can reach this API
# from any origin during initial deployment. allow_credentials must stay
# False while allow_origins is "*" — browsers reject that combination.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms.router)
app.include_router(movies.router)
app.include_router(ws.router)


@app.get("/health")
def health():
    return {"status": "ok"}
