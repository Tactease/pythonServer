from pydantic import BaseModel
from typing import List, Optional

class MissionModel(BaseModel):
    classId: int
    missionType: str
    startDate: str
    endDate: str
    soldierCount: int
    soldiersOnMission: Optional[List[str]] = []

    class Config:
        collection = "missions"