import sys
import os.path
from ortools.sat.python import cp_model
import json
from datetime import datetime, timedelta
from collections import defaultdict
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from functions import getMissions, getSoldiers, datetime_to_hours, hours_to_datetime

MIN_REST_HOURS = 6  # Minimal resting time in hours

def scheduleAlg(missionsInput, soldiersInput):
    
    print('inside python')
    missions_json = json.dumps(missionsInput)
    print('after jsonfiying missions')
    soldiers_json = json.dumps(soldiersInput)
    print('after jsonfiying soldiers')

    missions = getMissions(missions_json)
    print('after getMisions')

    soldiers = getSoldiers(soldiers_json)
    print('after getSoldiers')
    
    model = cp_model.CpModel()

    mission_intervals = {}
    # Create an IntervalVar for each mission
    for mission in missions:
        start_hours = datetime_to_hours(mission.startDate)
        end_hours = datetime_to_hours(mission.endDate)
        duration_hours = end_hours - start_hours
        missionId_key = str(mission.missionId)
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
            missionId_key = str(mission.missionId)
            soldierId_key = str(soldier.personalNumber)
            soldier_mission_vars[(soldierId_key, missionId_key)] = model.NewBoolVar(
                f'soldier_{soldierId_key}mission{missionId_key}'
        )


    # Constraint: Balance mission hours among soldiers as evenly as possible
   #             Calculate the total mission hours for each soldier

    soldier_total_hours = {str(soldier.personalNumber): model.NewIntVar(0, 24, f"total_hours_{str(soldier.personalNumber)}") for soldier in soldiers}
    mission_durations = {}
    for mission in missions:
        start_hours = datetime_to_hours(mission.startDate)
        end_hours = datetime_to_hours(mission.endDate)
        duration_hours = end_hours - start_hours
        missionId_key = str(mission.missionId)
        mission_intervals[missionId_key] = model.NewIntervalVar(start_hours, duration_hours, end_hours, f'mission_interval_{missionId_key}')
        mission_durations[missionId_key] = duration_hours

    # Calculate the total mission hours for each soldier
    soldier_total_hours = {str(soldier.personalNumber): model.NewIntVar(0, 24, f"total_hours_{str(soldier.personalNumber)}") for soldier in soldiers}
    for soldier in soldiers:
        soldier_id = str(soldier.personalNumber)
        total_hours_expr = [mission_durations[missionId_key] * soldier_mission_vars[(soldier_id, missionId_key)] for missionId_key in mission_durations.keys()]
        model.Add(soldier_total_hours[soldier_id] == sum(total_hours_expr))

    # Calculate the total number of missions assigned to each soldier
    soldier_mission_count = {str(soldier.personalNumber): model.NewIntVar(0, len(missions), f"mission_count_{str(soldier.personalNumber)}") for soldier in soldiers}
    for soldier in soldiers:
        soldier_id = str(soldier.personalNumber)
        count_expr = [soldier_mission_vars[(soldier_id, missionId_key)] for missionId_key in mission_durations.keys()]
        model.Add(soldier_mission_count[soldier_id] == sum(count_expr))

    # Define variables for the maximum and minimum total hours and mission counts
    max_hours_var = model.NewIntVar(0, 24, 'max_hours')
    min_hours_var = model.NewIntVar(0, 24, 'min_hours')
    max_mission_count = model.NewIntVar(0, len(missions), 'max_mission_count')
    min_mission_count = model.NewIntVar(0, len(missions), 'min_mission_count')

    # Constraints to set max and min values correctly
    for hours in soldier_total_hours.values():
        model.Add(max_hours_var >= hours)
        model.Add(min_hours_var <= hours)
        
    for count in soldier_mission_count.values():
        model.Add(max_mission_count >= count)
        model.Add(min_mission_count <= count)
        
    model.Add(max_hours_var - min_hours_var <= 3)

    # Objective: Minimize the difference to balance the workload and the number of missions
    model.Minimize(max_hours_var - min_hours_var + (max_mission_count - min_mission_count))



        # end of constraint fair durations

    def dis_en_able_constraints(flag, action):
        flag = action


    # Constraint: Each mission must be assigned at least one soldier and by required soldiers number for the mission
    for missionId_key, interval_var in mission_intervals.items():
        required_soldiers = next((mission.soldierCount for mission in missions if str(
            mission.missionId) == missionId_key), None)
        if required_soldiers is not None:
            model.Add(sum(soldier_mission_vars[(str(
                soldier.personalNumber), missionId_key)] for soldier in soldiers) == required_soldiers)


    # constraint: a soldier cannot be assigned to more than 1 mission at a time:
    def missions_overlap(mission1_id, mission2_id):
        start1, end1 = mission_intervals[mission1_id].StartExpr(), mission_intervals[mission1_id].EndExpr()
        start2, end2 = mission_intervals[mission2_id].StartExpr(), mission_intervals[mission2_id].EndExpr()
        return (((start1 < end2) and (start2 < end1)) or (start1 == end2) or (start2 == end1))


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
        avarage_mission_hours_for_soldier[date] = total_hours_per_day[date]/len(soldiers)

    for soldier in soldiers:
        for date, avg_hours in avarage_mission_hours_for_soldier.items():
            # Calculate the upper limit as 130% of the average hours
            upper_limit_hours = avg_hours * 1.3
            
            # Calculate the total hours assigned to the soldier for this date
            soldier_hours_for_date = []
            for mission in missions_by_date[date]:  # Assuming missions_by_date is available
                mission_id = str(mission.missionId)
                if (soldier.personalNumber, mission_id) in soldier_mission_vars:
                    duration_hours = datetime_to_hours(mission.endDate) - datetime_to_hours(mission.startDate)
                    assigned_var = soldier_mission_vars[(soldier.personalNumber, mission_id)]
                    soldier_hours_for_date.append(assigned_var * duration_hours)
                    
            if soldier_hours_for_date:  # If there are missions assigned to the soldier on this date
                total_hours_for_date = sum(soldier_hours_for_date)
                # Add constraint for total hours to be at least the average and not exceed the upper limit
                model.Add(total_hours_for_date >= avg_hours)
                model.Add(total_hours_for_date <= upper_limit_hours)

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


    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    dataTosend = {}
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        missionJson = []
        for mission in missions:
            missionId_key = str(mission.missionId)
            if missionId_key in mission_intervals:
                assigned_soldiers = []
                for soldier in soldiers:
                    soldierId_key = str(soldier.personalNumber)
                    if solver.BooleanValue(soldier_mission_vars[(soldierId_key, missionId_key)]):
                        assigned_soldiers.append(soldier.personalNumber)
                missionJson.append({missionId_key: assigned_soldiers})
        dataTosend = missionJson;
    else:
        dataTosend = {"error": "No solution was found:\n" + solver.ResponseStats()}

    result = json.dumps(dataTosend)
    return result
