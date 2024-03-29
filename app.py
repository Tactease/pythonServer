from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.missionsRouter import missionsRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(missionsRouter, prefix="/missions")


@app.get("/")
def root():
    return {"message": "Hello World"}
