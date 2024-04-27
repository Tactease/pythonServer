import json
import logging

from algorithm.parse_functions import getMissions, getSoldiers
from algorithm.soldiers_availability_funcs import find_available_soldiers

# Initialize logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

def add_multiple_missions_with_soldiers(schedule_json_str, new_missions, soldiers_json):
    try:
        original_schedule = getMissions(json.loads(schedule_json_str))
        new_missions = getMissions(json.loads(new_missions))
        soldiers = getSoldiers(json.loads(soldiers_json))
        
        temporary_schedule = original_schedule.copy()
        results = []
        new_messions_to_add = []
        for new_mission in new_missions:
            available_soldiers = find_available_soldiers(temporary_schedule, new_mission, soldiers)
            needed_soldiers_count = new_mission.soldierCount
            available_soldiers_list = list(available_soldiers)

            if needed_soldiers_count is not None and len(available_soldiers_list) >= needed_soldiers_count:
                selected_soldiers = available_soldiers_list[:needed_soldiers_count]
                new_mission.soldiersOnMission = selected_soldiers
                temporary_schedule.append(new_mission)
                new_messions_to_add.append(new_mission)
                results.append({"_id": new_mission._id, "status": "added"})
            else:
                print(f"Error: Not enough available soldiers for the mission. Needed: {needed_soldiers_count}, Available: {len(available_soldiers_list)}")
                return {'error: Not enough available soldiers for the mission.'} 
            
        formatted_new_missions = []
        for mission in new_messions_to_add:
            formatted_mission = {
                "missionType": mission.missionType,
                "classId": mission.classId,
                "startDate": mission.startDate.strftime("%d/%m/%y %H:%M"),  # Convert datetime objects to string
                "endDate": mission.endDate.strftime("%d/%m/%y %H:%M"),  # Convert datetime objects to string
                "soldierCount": mission.soldierCount,  # The count of assigned soldiers
                "soldiersOnMission": selected_soldiers  # List of assigned soldier IDs
            }
            formatted_new_missions.append(formatted_mission)
            
        return json.dumps(formatted_new_missions, indent=4)
        
    except Exception as e:
        print(f"Error {e}")
        raise e
   
