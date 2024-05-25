import json
from flask import jsonify
import logging
from collections import defaultdict
from algorithm.errors.error_handler import internal_server_error, bad_request_error, not_found_error

from ortools.sat.python import cp_model
from algorithm.soldiers_availability_funcs import is_soldier_available_for_mission
from algorithm.parse_functions import getMissions, getSoldiers, datetime_to_hours

# Initialize logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

MIN_REST_HOURS = 6  # Minimal resting time in hours

def generate_mission_schedule(missions_arg, soldiers_arg):
    try:
        missions = getMissions(json.loads(missions_arg))
        soldiers = getSoldiers(json.loads(soldiers_arg))
    except Exception as e:
        return json.dumps({"error": "Error processing missions or soldiers data."})

    model = cp_model.CpModel()

    soldier_mission_vars = {}
    mission_durations = {}

    mission_intervals = {}
    for mission in missions:
        try:
            start_hours = datetime_to_hours(mission.startDate)
            end_hours = datetime_to_hours(mission.endDate)
            duration_hours = end_hours - start_hours
            missionId_key = str(mission._id)
            mission_intervals[missionId_key] = model.NewIntervalVar(start_hours, duration_hours, end_hours,
                                                                    f'mission_interval_{missionId_key}')
            mission_durations[missionId_key] = duration_hours
        except Exception as e:
            return json.dumps({"error": "Error processing missions or soldiers data."})

        for soldier in soldiers:
            soldierId_key = str(soldier.personalNumber)
            if is_soldier_available_for_mission(soldier, mission.startDate, mission.endDate):
                soldier_mission_vars[(soldierId_key, missionId_key)] = model.NewBoolVar(
                    f'soldier_{soldierId_key}_mission_{missionId_key}')
            else:
                soldier_mission_vars[(soldierId_key, missionId_key)] = model.NewConstant(False)

    # Constraint: Each mission must be assigned at least the required number of soldiers
    for missionId_key, interval_var in mission_intervals.items():
        required_soldiers = next((mission.soldierCount for mission in missions if str(mission._id) == missionId_key), None)
        if required_soldiers is not None:
            model.Add(sum(soldier_mission_vars[(str(soldier.personalNumber), missionId_key)] for soldier in soldiers) == required_soldiers)

    # Constraint: Soldiers must have a minimum rest period between missions
    for soldier in soldiers:
        soldier_id = str(soldier.personalNumber)
        for mission1_id in mission_intervals.keys():
            for mission2_id in mission_intervals.keys():
                if mission1_id < mission2_id:  # To avoid redundant checks and self-comparison
                    start1, end1 = mission_intervals[mission1_id].StartExpr(), mission_intervals[mission1_id].EndExpr()
                    start2, end2 = mission_intervals[mission2_id].StartExpr(), mission_intervals[mission2_id].EndExpr()
                    
                    # Ensure rest period
                    model.AddBoolOr([
                        soldier_mission_vars[(soldier_id, mission1_id)].Not(),
                        soldier_mission_vars[(soldier_id, mission2_id)].Not(),
                        start2 - end1 >= MIN_REST_HOURS,
                        start1 - end2 >= MIN_REST_HOURS
                    ])

    try:
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
    except Exception as e:
        print(f"Error solving model: {e}")
        return json.dumps({"error": "Error solving model."})

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        formatted_schedule = []
        for mission in missions:
            missionId_key = str(mission._id)
            if missionId_key in mission_intervals:
                assigned_soldiers = [str(soldier.personalNumber) for soldier in soldiers if solver.BooleanValue(soldier_mission_vars[(str(soldier.personalNumber), missionId_key)])]
                formatted_mission = {
                    "missionType": mission.missionType,
                    "classId": mission.classId,
                    "startDate": mission.startDate.strftime("%d/%m/%Y %H:%M"),
                    "endDate": mission.endDate.strftime("%d/%m/%Y %H:%M"),
                    "soldierCount": len(assigned_soldiers),
                    "soldiersOnMission": assigned_soldiers
                }
                formatted_schedule.append(formatted_mission)

        schedule_json_str = json.dumps(formatted_schedule, indent=4)
        return schedule_json_str
    else:
        return json.dumps({"error": "No solution was found."})
