from collections import defaultdict
from datetime import datetime


# Functions from generate_schedule file
def sum_mission_hours_per_day(missions):
    missions_by_date = defaultdict(list)
    total_hours_per_day = defaultdict(int)

    for mission in missions:
        # Assuming missions is a list of dictionaries with startDate and endDate in "%d/%m/%Y %H:%M" format
        date_key = mission['startDate'].split(' ')[0]  # Extract just the date part
        start_hours = datetime_to_hours(mission['startDate'])
        end_hours = datetime_to_hours(mission['endDate'])
        duration_hours = end_hours - start_hours
        missions_by_date[date_key].append(duration_hours)

    for date, durations in missions_by_date.items():
        total_hours_per_day[date] = sum(durations)

    return total_hours_per_day


def dis_en_able_constraints(flag, action):
    flag = action


# Functions from algFunctions file

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


def calculate_duration(start, end):
    fmt = '%d/%m/%Y %H:%M'
    start_dt = datetime.strptime(start, fmt)
    end_dt = datetime.strptime(end, fmt)
    return (end_dt - start_dt).total_seconds() / 3600


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


def find_unassigned_soldiers(schedule_json_str, mission):
    schedule = json.loads(schedule_json_str)

    new_mission_start_dt = mission.startDate.strftime("%d/%m/%Y %H:%M")
    new_mission_end_dt = mission.endDate.strftime("%d/%m/%Y %H:%M")

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
    df_pivot = df.pivot_table(index="Soldier ID", columns="Date", values="Mission Time", aggfunc=lambda x: ', '.join(x),
                              fill_value="No mission")

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


# Functions from functions file

def hours_to_datetime(duration_hours):
    datetime_format = "%d/%m/%Y %H:%M"
    reference_datetime = datetime.strptime("01/01/2024 00:00", datetime_format)
    resulting_datetime = reference_datetime + timedelta(hours=duration_hours)
    return resulting_datetime.strftime(datetime_format)


def getRequests(requests_data):
    requests = []
    for request_data in requests_data:
        # Check if it's a MedicalRequest or PersonalRequest by checking for 'file' and 'fileName'
        if 'file' in request_data and 'fileName' in request_data:
            request = MedicalRequest(
                requestType=request_data["requestType"],
                daysOffType=request_data["daysOffType"],
                start_date=request_data["start_date"],
                end_date=request_data["end_date"],
                file=request_data["file"],
                fileName=request_data["fileName"]
            )
        elif 'note' in request_data:
            request = PersonalRequest(
                requestType=request_data["requestType"],
                daysOffType=request_data["daysOffType"],
                start_date=request_data["start_date"],
                end_date=request_data["end_date"],
                note=request_data["note"]
            )
        else:
            # Handle generic requests or log an error/warning
            request = Request(
                requestType=request_data["requestType"],
                daysOffType=request_data["daysOffType"],
                start_date=request_data["start_date"],
                end_date=request_data["end_date"]
            )
        requests.append(request)
    return requests


def parseRequests(requestList):
    requests = []
    for request_data in requestList:
        request = Request(
            requestType=request_data["requestType"],
            daysOffType=request_data["daysOffType"],
            start_date=request_data["startDate"],
            end_date=request_data["endDate"],
            note=request_data.get("note"),
            fileName=request_data.get("fileName")
        )
        requests.append(request)
    return requests



def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise e
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error: {e}")
        raise e
