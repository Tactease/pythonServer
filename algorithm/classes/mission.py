from datetime import datetime
from enum import Enum


class MissionType(Enum):
    PATROL_BY_FOOT = 1
    PATROL_BY_CAR = 2
    GUARD = 3
    WATCH = 4
    OPERATION = 5


class Mission:
    missionId_counter = 1  # Class variable to auto-increment missionId

    def __init__(self, missionId, missionType, classId, startDate, endDate, soldierCount, soldiersOnMission=[]):
        self._id = missionId
        self.missionType = missionType
        self.classId = classId
        self.startDate = datetime.strptime(startDate, "%d/%m/%Y %H:%M")
        self.endDate = datetime.strptime(endDate, "%d/%m/%Y %H:%M")
        self.soldierCount = soldierCount
        self.soldiersOnMission = soldiersOnMission

        Mission.missionId_counter += 1  # Increment the ID for the next mission

    def __str__(self):
        return f"missionType: {self.missionType} (startDate: {self.startDate}, endDate: {self.endDate}, soldierCount: {self.soldierCount}, soldiersOnMission: {self.soldiersOnMission})"
    
    def createMission(self, missionType, start_date, end_date, soldiers):
        # This might be redundant as the init method already creates a mission
        return Mission(missionType, start_date, end_date, soldiers)

    def getMissionId(self):
        return self._id

    def getMissionType(self):
        return self.missionType

    def getMissionHourLength(self):
        return (self.endDate - self.startDate).total_seconds() / 3600

    def getSoldierOnMission(self):
        return self.soldiersOnMission

    def updateSoldiers(self, updatedsoldiersOnMission):
        self.soldiersOnMission = updatedsoldiersOnMission
        self.soldiersCount = len(updatedsoldiersOnMission)
        
    def contains_soldier(self, personalNumber):
        return str(personalNumber) in (str(s) for s in self.soldiersOnMission)
