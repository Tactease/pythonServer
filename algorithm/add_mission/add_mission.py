import json
import logging

from algorithm.parse_functions import getMissions, getSoldiers
from algorithm.soldiers_availability_funcs import find_available_soldiers

# Initialize logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

def add_multiple_missions_with_soldiers(schedule_json_str, new_missions, soldiers_json):
    original_schedule = json.loads(schedule_json_str)
    temporary_schedule = original_schedule.copy()  # Work on a copy of the schedule
    soldiers = json.loads(soldiers_json)

    results = []
    for new_mission in new_missions:
        available_soldiers = find_available_soldiers(temporary_schedule, new_mission, soldiers)
        needed_soldiers_count = new_mission.get("soldierCount")
        available_soldiers_list = list(available_soldiers)

        if needed_soldiers_count is not None and len(available_soldiers_list) >= needed_soldiers_count:
            selected_soldiers = available_soldiers_list[:needed_soldiers_count]
            new_mission.soldiersOnMission = selected_soldiers
            temporary_schedule.append(new_mission)  # Add new mission to the temporary schedule
            results.append({"missionID": new_mission.missionId, "status": "added"})
        else:
            results.append({"missionID": new_mission.missionId, "status": "not enough soldiers", "available": len(available_soldiers_list)})
            print(f"Failed to add mission {new_mission.missionId} due to insufficient soldiers. Rolling back all changes.")
            return json.dumps(original_schedule, indent=4), results  # Return original schedule unchanged

    # If all missions added successfully
    updated_schedule_json_str = json.dumps(temporary_schedule, indent=4)
    return updated_schedule_json_str, results
