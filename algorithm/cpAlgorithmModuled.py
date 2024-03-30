import json
import logging
from collections import defaultdict

from ortools.sat.python import cp_model

from .algFunctions import add_new_mission_with_soldiers
from .functions import getMissions, getSoldiers, datetime_to_hours

# Initialize logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

MIN_REST_HOURS = 6  # Minimal resting time in hours


def is_soldier_available_for_mission(soldier, mission_start, mission_end):
    for request in soldier.requestsList:
        # Check if the mission's time period overlaps with any of the soldier's requests
        if not (mission_end <= request.start_date or mission_start >= request.end_date):
            return False  # Soldier is not available if any request overlaps with the mission
    return True


def generate_mission_schedule(missions_arg, soldiers_arg):
    try:
        missions = getMissions(json.loads(missions_arg))
        soldiers = getSoldiers(json.loads(soldiers_arg))
    except Exception as e:
        print(f"Error processing missions or soldiers data: {e}")
        return json.dumps({"error": "Failed to process missions or soldiers data."})

    model = cp_model.CpModel()

    mission_intervals = {}
    soldier_mission_vars = {}
    mission_durations = {}

    for mission in missions:
        start_hours = datetime_to_hours(mission.startDate)
        end_hours = datetime_to_hours(mission.endDate)
        duration_hours = end_hours - start_hours
        missionId_key = str(mission._id)
        mission_intervals[missionId_key] = model.NewIntervalVar(start_hours, duration_hours, end_hours,
                                                                f'mission_interval_{missionId_key}')
        mission_durations[missionId_key] = duration_hours

        for soldier in soldiers:
            soldierId_key = str(soldier.personalNumber)
            # Check if soldier is available for the mission considering their requests
            if is_soldier_available_for_mission(soldier, mission.startDate, mission.endDate):
                soldier_mission_vars[(soldierId_key, missionId_key)] = model.NewBoolVar(
                    f'soldier_{soldierId_key}mission{missionId_key}')
            else:
                # Soldier is not available, so we explicitly set this variable to False
                soldier_mission_vars[(soldierId_key, missionId_key)] = model.NewConstant(False)

    mission_intervals = {}
    # Create an IntervalVar for each mission
    for mission in missions:
        start_hours = datetime_to_hours(mission.startDate)
        end_hours = datetime_to_hours(mission.endDate)
        duration_hours = end_hours - start_hours
        missionId_key = str(mission._id)
        mission_intervals[missionId_key] = model.NewIntervalVar(
            start_hours,  # Start
            duration_hours,  # Size
            end_hours,  # End
            f'mission_interval_{missionId_key}'  # Name
        )

    # Create a BoolVar for each soldier-mission pair
    soldier_mission_vars = {}
    for soldier in soldiers:
        for mission in missions:
            missionId_key = str(mission._id)
            soldierId_key = str(soldier.personalNumber)
            soldier_mission_vars[(soldierId_key, missionId_key)] = model.NewBoolVar(
                f'soldier_{soldierId_key}mission{missionId_key}'
            )

    ########################## try: constraint: fair durations: ##########################

    # Constraint: Balance mission hours among soldiers as evenly as possible
    #             Calculate the total mission hours per day

    total_mission_hours = sum(mission_durations.values())
    total_soldier_count = sum(mission.soldierCount for mission in missions)
    if total_soldier_count > 0:
        fair_share_hours_per_soldier = total_mission_hours / total_soldier_count
    else:
        logging.warning("No soldiers counted for missions, setting fair share hours per soldier to 0.")
        fair_share_hours_per_soldier = 0  # Handle case where there are no soldiers required

    # First, calculate the total hours assigned to each soldier
    total_hours_per_soldier = {soldier_id: model.NewIntVar(0, 24 * len(missions), f"total_hours_{soldier_id}") for
                               soldier_id in [str(s.personalNumber) for s in soldiers]}
    # Calculate the total duration of missions each soldier is assigned to
    for soldier_id in total_hours_per_soldier:
        soldier_missions_duration = [soldier_mission_vars[(soldier_id, mission_id)] * mission_durations[mission_id] for
                                     mission_id, _ in soldier_mission_vars.keys() if soldier_id in soldier_mission_vars]
        model.Add(total_hours_per_soldier[soldier_id] >= round(fair_share_hours_per_soldier))

    ########################## end of constraint #################################
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

    #     soldier_total_hours = {str(soldier.personalNumber): model.NewIntVar(0, 24, f"total_hours_{str(soldier.personalNumber)}") for soldier in soldiers}
    #     mission_durations = {}
    #     for mission in missions:
    #         start_hours = datetime_to_hours(mission.startDate)
    #         end_hours = datetime_to_hours(mission.endDate)
    #         duration_hours = end_hours - start_hours
    #         missionId_key = str(mission.missionId)
    #         mission_intervals[missionId_key] = model.NewIntervalVar(start_hours, duration_hours, end_hours, f'mission_interval_{missionId_key}')
    #         mission_durations[missionId_key] = duration_hours

    # # Calculate the total mission hours for each soldier
    # soldier_total_hours = {str(soldier.personalNumber): model.NewIntVar(0, 24, f"total_hours_{str(soldier.personalNumber)}") for soldier in soldiers}
    # for soldier in soldiers:
    #     soldier_id = str(soldier.personalNumber)
    #     total_hours_expr = [mission_durations[missionId_key] * soldier_mission_vars[(soldier_id, missionId_key)] for missionId_key in mission_durations.keys()]
    #     model.Add(soldier_total_hours[soldier_id] == sum(total_hours_expr))

    # # Calculate the total number of missions assigned to each soldier
    # # soldier_mission_count = {str(soldier.personalNumber): model.NewIntVar(0, len(missions), f"mission_count_{str(soldier.personalNumber)}") for soldier in soldiers}
    # # for soldier in soldiers:
    # #     soldier_id = str(soldier.personalNumber)
    # #     count_expr = [soldier_mission_vars[(soldier_id, missionId_key)] for missionId_key in mission_durations.keys()]
    # #     model.Add(soldier_mission_count[soldier_id] == sum(count_expr))

    # # Define variables for the maximum and minimum total hours and mission counts
    # max_hours_var = model.NewIntVar(0, 24, 'max_hours')
    # min_hours_var = model.NewIntVar(0, 24, 'min_hours')
    # # max_mission_count = model.NewIntVar(0, len(missions), 'max_mission_count')
    # # min_mission_count = model.NewIntVar(0, len(missions), 'min_mission_count')

    # # Constraints to set max and min values correctly

    # model.Add(max_hours_var - min_hours_var <= 3)

    # # Objective: Minimize the difference to balance the workload and the number of missions
    # model.Minimize(max_hours_var - min_hours_var)

    # end of constraint fair durations

    def dis_en_able_constraints(flag, action):
        flag = action

    # Constraint: Each mission must be assigned at least one soldier and by required soldiers number for the mission
    for missionId_key, interval_var in mission_intervals.items():
        required_soldiers = next((mission.soldierCount for mission in missions if str(
            mission._id) == missionId_key), None)
        if required_soldiers is not None:
            model.Add(sum(soldier_mission_vars[(str(
                soldier.personalNumber), missionId_key)] for soldier in soldiers) == required_soldiers)

    # constraint: a soldier cannot be assigned to more than 1 mission at a time:
    # def missions_overlap(mission1_id, mission2_id):
    #     start1, end1 = mission_intervals[mission1_id].StartExpr(), mission_intervals[mission1_id].EndExpr()
    #     start2, end2 = mission_intervals[mission2_id].StartExpr(), mission_intervals[mission2_id].EndExpr()
    #     return (((start1 < end2) and (start2 < end1)) or (start1 == end2) or (start2 == end1))

    def missions_overlap(mission1, mission2):
        # Check if missions' data is valid before comparison
        try:
            start1, end1 = mission_intervals[mission1_id].StartExpr(), mission_intervals[mission1_id].EndExpr()
            start2, end2 = mission_intervals[mission2_id].StartExpr(), mission_intervals[mission2_id].EndExpr()
        except KeyError as e:
            logging.error(f"Missing mission start/end date: {e}")
            return False
        return not (end1 <= start2 or start1 >= end2)

    soldier_assigned_vars = {}
    for soldier in soldiers:
        soldier_id = str(soldier.personalNumber)
        # This variable is 1 if the soldier is assigned to any mission, 0 otherwise
        soldier_assigned_vars[soldier_id] = model.NewBoolVar(f'soldier_assigned_{soldier_id}')

        ##########################
        # constraint : Soldiers should be assigned equally

    total_mission_hours = sum(mission_durations.values())
    missions_by_date = defaultdict(list)
    for mission in missions:
        # Convert start datetime to date (YYYY-MM-DD) for grouping
        start_date = mission.startDate.date()
        missions_by_date[start_date].append(mission)

    total_hours_per_day = {}
    avarage_mission_hours_for_soldier = {}
    for date, missions_on_date in missions_by_date.items():
        total_hours = 0
        for mission in missions_on_date:
            start_hours = datetime_to_hours(mission.startDate)
            end_hours = datetime_to_hours(mission.endDate)
            duration_hours = end_hours - start_hours
            total_hours += duration_hours
        total_hours_per_day[date] = total_hours
        avarage_mission_hours_for_soldier[date] = total_hours_per_day[date] / len(soldiers)
    # print(avarage_mission_hours_for_soldier)

    for soldier in soldiers:
        for date, avg_hours in avarage_mission_hours_for_soldier.items():
            # Calculate the upper limit as 130% of the average hours
            upper_limit_hours = avg_hours * 1.3

            # Calculate the total hours assigned to the soldier for this date
            soldier_hours_for_date = []
            for mission in missions_by_date[date]:  # Assuming missions_by_date is available
                mission_id = str(mission._id)
                if (soldier.personalNumber, mission_id) in soldier_mission_vars:
                    duration_hours = datetime_to_hours(mission.endDate) - datetime_to_hours(mission.startDate)
                    assigned_var = soldier_mission_vars[(soldier.personalNumber, mission_id)]
                    soldier_hours_for_date.append(assigned_var * duration_hours)

            if soldier_hours_for_date:  # If there are missions assigned to the soldier on this date
                total_hours_for_date = sum(soldier_hours_for_date)
                # Add constraint for total hours to be at least the average and not exceed the upper limit
                model.Add(total_hours_for_date >= avg_hours)
                model.Add(total_hours_for_date <= upper_limit_hours)

        #####################################

        # end of constraint fair durations


    for soldier in soldiers:
        soldier_id = str(soldier.personalNumber)
        for mission1_id in mission_intervals.keys():
            for mission2_id in mission_intervals.keys():
                if mission1_id < mission2_id:  # To avoid redundant checks and self-comparison
                    if missions_overlap(mission1_id, mission2_id):
                        # Ensuring a soldier cannot be assigned to both missions if they overlap
                        model.AddBoolOr([
                            soldier_mission_vars[(soldier_id, mission1_id)].Not(),
                            soldier_mission_vars[(soldier_id, mission2_id)].Not()
                        ])

    try:
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
    except Exception as e:
        print(f"Error solving model: {e}")
        return json.dumps({"error": "Failed to solve the model."})

    # mission_schedule = []

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        formatted_schedule = []  # Initialize an empty list for the formatted schedule
        for mission in missions:
            missionId_key = str(mission._id)
            if missionId_key in mission_intervals:
                assigned_soldiers = [str(soldier.personalNumber) for soldier in soldiers if solver.BooleanValue(
                    soldier_mission_vars[(str(soldier.personalNumber), missionId_key)])]
                # Create a dictionary for the mission with the desired format
                formatted_mission = {
                    "missionType": mission.missionType,
                    "classId": mission.classId,
                    "startDate": mission.startDate.strftime("%d/%m/%Y %H:%M"),  # Convert datetime objects to string
                    "endDate": mission.endDate.strftime("%d/%m/%Y %H:%M"),  # Convert datetime objects to string
                    "soldierCount": len(assigned_soldiers),  # The count of assigned soldiers
                    "soldiersOnMission": assigned_soldiers  # List of assigned soldier IDs
                }
                formatted_schedule.append(formatted_mission)

        # Convert the list of formatted missions to a JSON string with indentation for readability
        schedule_json_str = json.dumps(formatted_schedule, indent=4)
        return schedule_json_str
    else:
        return json.dumps({"error": "No solution was found."})


def main():
    with open(
            'C:/Users/adler/OneDrive - Shenkar College/SCHOOL/Year3SM1/שיטות בהנדסת תוכנה/Tactease/algorithm/temp-missions.json',
            'r') as file:
        missions_json_str = file.read()
    with open(
            'C:/Users/adler/OneDrive - Shenkar College/SCHOOL/Year3SM1/שיטות בהנדסת תוכנה/Tactease/algorithm/temp-soldiers.json',
            'r') as file:
        soldiers_json_str = file.read()

    missions = getMissions(json.loads(missions_json_str))
    schedule__json = generate_mission_schedule(missions_json_str, soldiers_json_str)

    print("New mission is added")
    new_mission_details = {
        "_id": len(missions) + 1,
        "startDate": "12/02/2024 10:00",
        "endDate": "12/02/2024 14:00",
        "soldierCount": 6
    }

    updated_schedule_json_str = add_new_mission_with_soldiers(schedule__json, new_mission_details, soldiers_json_str)
    print(updated_schedule_json_str)
    # print_as_table(schedule__json)


if __name__ == "__main__":
    main()
