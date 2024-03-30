import json
import logging

from algorithm.parse_functions import getMissions, getSoldiers
from algorithm.soldiers_availability_funcs import find_available_soldiers

# Initialize logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')


def add_new_mission_with_soldiers(schedule_json_str, new_mission, soldiers_json):
    try:
        missions = getMissions(json.loads(schedule_json_str))
        new_missions_details = getMissions(json.loads(new_mission))
        soldiers = getSoldiers(json.loads(soldiers_json))

        # Attempt to find available soldiers for the new mission
        available_soldiers = find_available_soldiers(missions, new_missions_details, soldiers)

        # Convert available_soldiers from a set to a list for slicing
        available_soldiers_list = list(available_soldiers)

        needed_soldiers_count = new_missions_details[0].soldierCount

        # Proceed only if the exact number of needed soldiers is available or more
        if needed_soldiers_count is not None and len(available_soldiers_list) >= needed_soldiers_count:
            # Select only the needed amount of soldiers if more are available
            selected_soldiers = available_soldiers_list[:needed_soldiers_count]
        else:
            # Handle the case where not enough soldiers are available
            print(
                f"Error: Not enough available soldiers for the mission. Needed: {needed_soldiers_count}, Available: {len(available_soldiers_list)}")
            return {'error: Not enough available soldiers for the mission.'}  # or handle this case as needed

        # Assign the selected soldiers to the new mission and add it to the schedule
        formatted_schedule = []
        for mission in new_missions_details:
            formatted_mission = {
                "missionType": mission.missionType,
                "classId": mission.classId,
                "startDate": mission.startDate.strftime("%d/%m/%Y %H:%M"),  # Convert datetime objects to string
                "endDate": mission.endDate.strftime("%d/%m/%Y %H:%M"),  # Convert datetime objects to string
                "soldierCount": mission.soldierCount,  # The count of assigned soldiers
                "soldiersOnMission": selected_soldiers  # List of assigned soldier IDs
            }
            formatted_schedule.append(formatted_mission)

        # missions.append(new_mission)

        return json.dumps(formatted_schedule, indent=4)
    except Exception as e:
        print(f"Error {e}")
        raise e
