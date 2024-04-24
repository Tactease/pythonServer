from datetime import datetime, timedelta
import json
import pandas as pd
from collections import defaultdict
from .functions import datetime_to_hours



def parse_datetime(date_str):
    return datetime.strptime(date_str, '%d/%m/%Y %H:%M')


def calculate_duration(start, end):
    fmt = '%d/%m/%Y %H:%M'
    start_dt = datetime.strptime(start, fmt)
    end_dt = datetime.strptime(end, fmt)
    return (end_dt - start_dt).total_seconds() / 3600


def update_mission_schedule(schedule_json_str, missionID, soldier_to_add, soldier_to_remove):
    # Load the schedule from JSON
    missions = json.loads(schedule_json_str)
    
    # Find the mission by missionID and replace the soldier
    for mission in missions:
        if mission["missionId"] == missionID:
            try:
                # Find the index of the soldier to remove
                index_to_replace = mission["soldiersOnMission"].index(str(soldier_to_remove))
                # Replace the soldier
                mission["soldiersOnMission"][index_to_replace] = str(soldier_to_add)
                print(f"Soldier {soldier_to_remove} replaced by {soldier_to_add} in mission {missionID}")
            except ValueError:
                print(f"Soldier {soldier_to_remove} not found in mission {missionID}")
            break
    
    # Return the updated missions as a JSON string (if you need to save it back to a file or further process)
    return json.dumps(missions, indent=4)


def calculate_solder_mission_hours(missions):
    soldier_mission_hours = {}
    for mission in missions:
        mission_duration = calculate_duration(mission.startDate, mission.endDate)
        mission_day = datetime.strptime(mission.startDate, '%d/%m/%Y %H:%M').date()
        
        for soldier_number in mission.soldiersOnMission:
            if soldier_number not in soldier_mission_hours:
                soldier_mission_hours[soldier_number] = {}
            if mission_day not in soldier_mission_hours[soldier_number]:
                soldier_mission_hours[soldier_number][mission_day] = 0
            soldier_mission_hours[soldier_number][mission_day] += mission_duration
    return soldier_mission_hours  # Ensure this dictionary is returned

def find_available_soldiers(schedule, newMission, soldiers):
    new_mission_start = parse_datetime(newMission["startDate"])
    new_mission_end = parse_datetime(newMission["endDate"])
    rest_period = timedelta(hours=12)  # Set the rest period (for example, 12 hours)
    available_soldiers = set()

    all_soldiers_info = {soldier["personalNumber"]: soldier for soldier in soldiers}
    all_soldiers = set(all_soldiers_info.keys())

    for soldier_id in all_soldiers:
        soldier = all_soldiers_info[soldier_id]
        soldier_is_available = True
        
        # Check for mission schedule conflicts
        for mission in schedule:
            if soldier_id in mission["soldiersOnMission"]:
                mission_start = parse_datetime(mission["startDate"])
                mission_end = parse_datetime(mission["endDate"])
                # Adjusted to include rest period in the check
                if not (new_mission_end + rest_period <= mission_start or new_mission_start >= mission_end + rest_period):
                    soldier_is_available = False
                    break
        
        # Check for personal requests conflicts
        if soldier_is_available:
            for request in soldier.get("requestList", []):
                request_start = parse_datetime(request["startDate"])
                request_end = parse_datetime(request["endDate"])
                # Ensure new mission does not overlap with personal requests
                if not (new_mission_end <= request_start or new_mission_start >= request_end):
                    soldier_is_available = False
                    break
        
        if soldier_is_available:
            available_soldiers.add(soldier_id)

    return available_soldiers



def find_unassigned_soldiers(schedule_json_str, new_mission):
    schedule = json.loads(schedule_json_str)
    
    new_mission_start_dt = mission.startDate.strftime("%d/%m/%Y %H:%M")
    new_mission_end_dt =  mission.endDate.strftime("%d/%m/%Y %H:%M")
    
    assigned_soldiers = set()
    
    # Iterate through existing missions to check for overlaps
    for mission in schedule:
        mission_start = mission.startDate.strftime("%d/%m/%Y %H:%M")
        mission_end = mission.endDate.strftime("%d/%m/%Y %H:%M")
        
        if not (new_mission_end_dt <= mission_start or new_mission_start_dt >= mission_end):
            assigned_soldiers.update(mission.get('soldiersOnMission', []))
    
    # Find all unique soldiers in the schedule
    all_soldiers = set(soldier for mission in schedule for soldier in mission.get('soldiersOnMission', []))
    
    # Determine unassigned soldiers by subtracting assigned soldiers from all soldiers
    unassigned_soldiers = all_soldiers - assigned_soldiers
    
    return list(unassigned_soldiers)


def add_new_mission_with_soldiers(schedule_json_str, new_mission_details, soldiers_json):
    missions = json.loads(schedule_json_str)
    soldiers = json.loads(soldiers_json)
    
    if isinstance(soldiers_json, str):
        soldiers = json.loads(soldiers_json)
    else:
        soldiers = soldiers_json

    # Attempt to find available soldiers for the new mission
    available_soldiers = find_available_soldiers(missions, new_mission_details, soldiers)

    # Convert available_soldiers from a set to a list for slicing
    available_soldiers_list = list(available_soldiers)

    needed_soldiers_count = new_mission_details.get("soldierCount")

    # Proceed only if the exact number of needed soldiers is available or more
    if needed_soldiers_count is not None and len(available_soldiers_list) >= needed_soldiers_count:
        # Select only the needed amount of soldiers if more are available
        selected_soldiers = available_soldiers_list[:needed_soldiers_count]
    else:
        # Handle the case where not enough soldiers are available
        print(f"Error: Not enough available soldiers for the mission. Needed: {needed_soldiers_count}, Available: {len(available_soldiers_list)}")
        return None  # or handle this case as needed

    # Assign the selected soldiers to the new mission and add it to the schedule
    new_mission_details["soldiersOnMission"] = selected_soldiers
    missions.append(new_mission_details)

    return json.dumps(missions, indent=4)

def pre_check_soldier_availability_for_all_missions(missions, soldiers, schedule):
    all_checks = []
    for mission in missions:
        available_soldiers = find_available_soldiers(schedule, mission, soldiers)
        needed = mission.get("soldierCount", 0)
        if len(available_soldiers) < needed:
            all_checks.append(False)
        else:
            all_checks.append(True)
    return all(all_checks)  # Returns True if all missions can be scheduled

def add_checked_missions(schedule_json_str, new_missions, soldiers_json):
    schedule = json.loads(schedule_json_str)
    soldiers = json.loads(soldiers_json)
    
    # Check if all missions can be successfully scheduled
    if not pre_check_soldier_availability_for_all_missions(new_missions, soldiers, schedule):
        print("Not all missions can be scheduled. No changes will be made.")
        return schedule_json_str, [{"missionID": mission["missionId"], "status": "not scheduled"} for mission in new_missions]
    
    # If check is successful, proceed with adding missions
    results = []
    for mission in new_missions:
        # This part will always succeed since we pre-checked
        available_soldiers = find_available_soldiers(schedule, mission, soldiers)
        selected_soldiers = list(available_soldiers)[:mission["soldierCount"]]
        mission["soldiersOnMission"] = selected_soldiers
        schedule.append(mission)
        results.append({"missionID": mission["missionId"], "status": "added"})
    
    updated_schedule_json_str = json.dumps(schedule, indent=4)
    return updated_schedule_json_str, results



def find_min_hours_soldiers_for_day(soldier_mission_hours, specific_day):
    # Collect all soldiers and their hours for the specific day
    soldiers_hours = []
    for soldier, days in soldier_mission_hours.items():
        if specific_day in days:
            soldiers_hours.append((soldier, days[specific_day]))
    
    # Sort the list by hours in ascending order
    soldiers_hours.sort(key=lambda x: x[1])
    
    # Return the top 3 soldiers with the minimum hours, or all if less than 3
    return soldiers_hours[:3]

if __name__ == "_main_":
    # Assuming the rest of your setup remains the same...
    with open('C:/Users/adler/OneDrive - Shenkar College/SCHOOL/Year3SM1/שיטות בהנדסת תוכנה/Tactease/algorithm/temp-schedule.json', 'r') as file:
        schedule_json_str = file.read()
        
    updated_schedule_json_str = update_mission_schedule(schedule_json_str, 1, '1234567', '5555555')
    
    # print(updated_schedule_json_str)
        
    missions = json.loads(schedule_json_str)
    soldier_mission_hours = calculate_solder_mission_hours(missions)
    
    specific_day = datetime(2024, 2, 12).date()  # Specify the day to check
    results = find_min_hours_soldiers_for_day(soldier_mission_hours, specific_day)
    
    if results:
        for i, (soldier, hours) in enumerate(results, start=1):
            print(f"{i}. Soldier {soldier} with {hours} hours on {specific_day}")
    else:
        print(f"No mission data available for {specific_day}")
        

def print_as_table(schedule_json):
    # Parse the JSON string into a Python object
    schedule = json.loads(schedule_json)
    
    data = []
    for mission in schedule:
        start_date = datetime.strptime(mission["startDate"], "%d/%m/%Y %H:%M").strftime("%Y-%m-%d")
        for soldier_id in mission["soldiersOnMission"]:
            start_time = datetime.strptime(mission["startDate"], "%d/%m/%Y %H:%M").strftime("%H:%M")
            end_time = datetime.strptime(mission["endDate"], "%d/%m/%Y %H:%M").strftime("%H:%M")
            data.append({
                "Soldier ID": soldier_id,
                "Date": start_date,
                "Mission Time": f"{start_time}-{end_time}"
            })
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Pivot the DataFrame to get the desired table format
    df_pivot = df.pivot_table(index="Soldier ID", columns="Date", values="Mission Time", aggfunc=lambda x: ', '.join(x), fill_value="No mission")
    
    # Print the table
    print(df_pivot)
    
def average_mission_time_per_soldier(missions):
    missions_by_date = defaultdict(list)
    soldier_count_by_date = defaultdict(int)
    
    for mission in missions:
        date_key = mission['startDate'].split(' ')[0]  # Extract just the date part
        start_hours = datetime_to_hours(mission['startDate'])
        end_hours = datetime_to_hours(mission['endDate'])
        duration_hours = end_hours - start_hours
        missions_by_date[date_key].append(duration_hours)
        soldier_count_by_date[date_key] += len(mission.get('soldiersOnMission', []))  # Count soldiers for each mission
    
    average_hours_per_soldier_per_day = {}
    for date, durations in missions_by_date.items():
        total_hours = sum(durations)
        # Avoid division by zero
        if soldier_count_by_date[date] > 0:
            average_hours_per_soldier_per_day[date] = total_hours / soldier_count_by_date[date]
        else:
            average_hours_per_soldier_per_day[date] = 0
    
    return average_hours_per_soldier_per_day