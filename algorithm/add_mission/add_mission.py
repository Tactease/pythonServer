import json
import logging

from algorithm.soldiers_availability_funcs import find_available_soldiers

# Initialize logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')


def add_new_mission_with_soldiers(schedule_json_str, new_mission, soldiers_json):
    try:
        missions = json.loads(schedule_json_str)
        soldiers = json.loads(soldiers_json)

        # missions = getMissions(json.loads(schedule_json_str))
        # new_missions_details = getMissions(json.loads(new_mission))
        # soldiers = getSoldiers(json.loads(soldiers_json))

        # Attempt to find available soldiers for the new mission
        available_soldiers = find_available_soldiers(missions, new_mission, soldiers)

        # Convert available_soldiers from a set to a list for slicing
        available_soldiers_list = list(available_soldiers)

        needed_soldiers_count = new_mission.get("soldierCount")

        # Proceed only if the exact number of needed soldiers is available or more
        if needed_soldiers_count is not None and len(available_soldiers_list) >= needed_soldiers_count:
            # Select only the needed amount of soldiers if more are available
            selected_soldiers = available_soldiers_list[:needed_soldiers_count]
        else:
            # Handle the case where not enough soldiers are available
            print(
                f"Error: Not enough available soldiers for the mission. Needed: {needed_soldiers_count}, Available: {len(available_soldiers_list)}")
            return None  # or handle this case as needed

        # Assign the selected soldiers to the new mission and add it to the schedule
        new_mission["soldiersOnMission"] = selected_soldiers
        missions.append(new_mission)

        return json.dumps(missions, indent=4)
    except Exception as e:
        print(f"Error {e}")
        raise e
