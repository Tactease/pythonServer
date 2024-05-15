import logging
from datetime import timedelta

from .parse_functions import parse_datetime

logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')


def is_soldier_available_for_mission(soldier, mission_start, mission_end):
    for request in soldier.requestsList:
        # Check if the mission's time period overlaps with any of the soldier's requests
        if request.status == 'Approved' and not (mission_end <= request.start_date or mission_start >= request.end_date):
            return False  # Soldier is not available if any request overlaps with the mission
    return True


def find_available_soldiers(schedule, new_mission, soldiers):
    # Assuming soldiers is already a Python list or dict, so no need to parse it from a string
    new_mission_start = new_mission.startDate
    new_mission_end = new_mission.endDate

    rest_period = timedelta(hours=4)
    available_soldiers = set()
    all_soldiers_info = {soldier.personalNumber: soldier for soldier in soldiers}
    all_soldiers = set(all_soldiers_info.keys())

    for soldier_id in all_soldiers:
        soldier = all_soldiers_info[soldier_id]
        soldier_is_available = True

        # Check for mission schedule conflicts
        for mission in schedule:
            if soldier_id in mission.soldiersOnMission:
                mission_start = mission.startDate
                mission_end = mission.endDate
                if not (
                        new_mission_end + rest_period <= mission_start or new_mission_start >= mission_end + rest_period):
                    soldier_is_available = False
                    break

        # Check for request conflicts
        if soldier_is_available:
            for request in soldier.requestsList:
                request_start = request.start_date
                request_end = request.end_date
                if request.status == 'Approved' and not (new_mission_end <= request_start or new_mission_start >= request_end):
                    soldier_is_available = False
                    break

        if soldier_is_available:
            available_soldiers.add(soldier_id)

    return available_soldiers
