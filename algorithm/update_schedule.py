import json
from flask import jsonify
import logging
from collections import defaultdict

# from errors.error_handler import internal_server_error, bad_request_error, not_found_error
from algorithm.parse_functions import getMissions, getSoldiers, parse_datetime
from algorithm.classes.request import getRequest
from algorithm.classes.soldier import Soldier
from datetime import datetime, timedelta

# with open('mock_missions.json', 'r') as missions_file:
#     schedule_json_str = missions_file.read()

# with open('mock_soldiers.json', 'r') as soldiers_file:
#     soldiers = soldiers_file.read()

import logging


class NoAvailableSoldiersException(Exception):
    """Exception raised when no available soldiers are found."""

    pass


def find_available_soldiers_no_requests(missions_arg, soldiers_arg, request_approved):
    soldiers = getSoldiers(soldiers_arg)
    personalNumber = request_approved["personalNumber"]
    index = request_approved["index"]
    # Find the unavailable soldier and the specific request
    unavailable_soldier = next(
        (s for s in soldiers if str(s.personalNumber) == str(personalNumber)), None
    )

    if not unavailable_soldier:
        raise ValueError("No soldier found with the given personal number.")

    unavailable_soldier = Soldier(
        personalNumber,
        unavailable_soldier.fullName,
        unavailable_soldier.classId,
        unavailable_soldier.className,
        unavailable_soldier.pakal,
        unavailable_soldier.requestsList,
    )
    request = unavailable_soldier.getSpecificRequest(index)

    request_start = request.startDate
    request_end = request.endDate

    # Find missions overlapping with the request
    overlapping_missions = [
        m
        for m in getMissions(missions_arg)
        if m.contains_soldier(personalNumber)
        and m.endDate >= request_start
        and m.startDate <= request_end
    ]

    # Find potential replacements
    replacements = []
    for mission in overlapping_missions:
        start_buffer = mission.startDate - timedelta(hours=6)
        end_buffer = mission.endDate + timedelta(hours=6)

        # Filter soldiers who are available for this time range
        for soldier in soldiers:
            if (
                soldier.personalNumber != personalNumber
                and not soldier.has_conflicting_requests(start_buffer, end_buffer)
                and not is_on_mission_during(
                    missions_arg, soldier, start_buffer, end_buffer
                )
            ):
                replacements.append(soldier.personalNumber)

    return list(set(replacements))  # Return unique soldier personal numbers


def is_on_mission_during(missions, soldier, start_buffer, end_buffer):
    for mission in missions:
        mission_start = mission.startDate
        mission_end = mission.endDate
        # Check if the soldier is on the mission and if there is an overlap with the buffer
        if soldier.personalNumber in mission.soldiersOnMission and not (
            mission_end <= start_buffer or mission_start >= end_buffer
        ):
            return True
    return False


def find_soldier_in_missions(missions, personal_number):
    missions_obj = missions
    matching_missions = []
    for mission in missions_obj:
        if personal_number in mission.soldiersOnMission:
            matching_missions.append(mission)
    if not matching_missions:
        print("no matching missions")
    return matching_missions


def find_matched_request(soldiers, personalNumber, index):
    for soldier in soldiers:
        if soldier.personalNumber == personalNumber:
            if 0 <= index <= len(soldier.requestsList):
                print("out if find_matched_request with request")
                return soldier.requestsList[index]
            else:
                return None
            # Soldier not found
    print("out of find_matched_request with none")
    return None


def change_soldier_upon_request_approved(missions_arg, soldiers_arg, request_approved):
    try:
        missions = getMissions(json.loads(missions_arg))
        soldiers = getSoldiers(json.loads(soldiers_arg))
        request_approved_dict = json.loads(request_approved)
        request_personal_num = str(request_approved_dict["personalNumber"])
    except Exception as e:
        return json.dumps({"error": str(e)})

    try:
        matched_request = find_matched_request(
            soldiers,
            request_approved_dict["personalNumber"],
            request_approved_dict["index"],
        )
        if not matched_request:
            return jsonify({"error": "Request not found"}), 400
    except Exception as e:
        return json.dumps({"error": str(e)})

    print(matched_request)

    buffer_start = matched_request.startDate - timedelta(days=3)
    buffer_end = matched_request.endDate + timedelta(days=3)

    # Find the missions the unavailable soldier is part of during the request period

    matching_missions = []
    for mission in missions:
        if (
            request_personal_num in mission.soldiersOnMission
            and mission.endDate >= matched_request.startDate
            and mission.startDate <= matched_request.endDate
        ):
            matching_missions.append(mission)

    for mission in matching_missions:
        print(mission)

    if not matching_missions:
        return json.dumps({"error": "No matching missions found."})

    # Calculate available soldiers and their mission times
    available_soldier_times = defaultdict(int)
    for mission in missions:
        for soldier_id in mission.soldiersOnMission:
            if soldier_id != request_approved_dict["personalNumber"]:
                for soldier in soldiers:
                    if soldier.personalNumber == soldier_id:
                        soldier = soldier
                if (
                    soldier
                    and not soldier.has_conflicting_requests(buffer_start, buffer_end)
                    and not is_on_mission_during(
                        missions,
                        soldier,
                        mission.startDate - timedelta(hours=6),
                        mission.endDate + timedelta(hours=6),
                    )
                ):
                    mission_duration = (
                        mission.endDate - mission.startDate
                    ).total_seconds() / 3600  # Convert to hours
                    available_soldier_times[soldier_id] += mission_duration

    # Select the soldier with the minimum mission time
    if available_soldier_times:
        minimal_soldier_id = min(
            available_soldier_times, key=available_soldier_times.get
        )
        print(
            f"Selected minimal mission time soldier: {minimal_soldier_id} with {available_soldier_times[minimal_soldier_id]} hours"
        )

        # Assign this soldier to all matching missions
        try:
            for mission in matching_missions:
                mission.soldiersOnMission.remove(request_personal_num)
                mission.soldiersOnMission.append(str(minimal_soldier_id))
                print(
                    f"Replaced soldier {request_approved_dict['personalNumber']} with {minimal_soldier_id} in mission {mission._id}"
                )

            print(matching_missions)
            formatted_new_missions = []
            for mission in matching_missions:
                formatted_mission = {
                    "_id": mission._id,
                    "missionType": mission.missionType,
                    "classId": mission.classId,
                    "startDate": mission.startDate.strftime(
                        "%d/%m/%Y %H:%M"
                    ),  # Convert datetime objects to string
                    "endDate": mission.endDate.strftime(
                        "%d/%m/%Y %H:%M"
                    ),  # Convert datetime objects to string
                    "soldierCount": mission.soldierCount,  # The count of assigned soldiers
                    "soldiersOnMission": [
                        str(soldier_id) for soldier_id in mission.soldiersOnMission
                    ],  # List of assigned soldier IDs converted to strings
                }
                formatted_new_missions.append(formatted_mission)

            return json.dumps(formatted_new_missions)
        except Exception as e:
            return json.dumps({"error": str(e)})
    else:
        print("No suitable replacement found.")
        data = {
            "message": "No suitable replacement found.",
        }
        return json.dumps(data)
