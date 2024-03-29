from datetime import datetime
from mission import Mission

class Schedule:
    scheduleId_counter = 1  # Class variable to auto-increment missionId
    
    def __init__(self, scheduleId, classId, end_date, soldiers=[]):
        self.scheduleId = Schedule.missionId_counter
        self.classId = classId
        self.missions = []

        Schedule.scheduleId_counter.missionId_counter += 1  # Increment the ID for the next mission
        
    def __addMission__(self, mission):
        newMission = {mission.getMissionId(): mission}
        self.missions.append(newMission)
    
    def getClassId(self):
        return self.classId
    
    def findMissionsOnDate(self, target_date):
            target_date = datetime.strptime(target_date, "%Y-%m-%d")
            matching_missions = []
            
            for mission_dict in self.missions:
                mission = list(mission_dict.values())[0]
                if mission.start_date.date() == target_date.date() or mission.end_date.date() == target_date.date():
                    matching_missions.append(mission)
            
            return matching_missions
        
    def findMissionById(self, mission_id):
        for mission_dict in self.missions:
            mission = list(mission_dict.values())[0]
            if mission.getMissionId() == mission_id:
                return mission
        return None         