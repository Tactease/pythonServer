from fastapi import APIRouter, HTTPException
from pythonServer.controllers.missionsController import missionsController

missionsRouter = APIRouter(
    prefix="/missions",
    tags=["missions"],
)

@missionsRouter.post("")
async def add_mission(mission):
    response = await missionsController.create_mission(mission)

    return response