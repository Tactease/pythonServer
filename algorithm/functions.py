import json
import logging
from datetime import datetime, timedelta

from .classes.mission import Mission
from .classes.request import Request, PersonalRequest, MedicalRequest
from .classes.soldier import Soldier

# Initialize logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')


def datetime_to_hours(datetime_input):
    try:
        """Function to convert datetime strings to a consistent unit (e.g., hours)"""
        datetime_format = "%d/%m/%Y %H:%M"
        reference_datetime = datetime.strptime("01/01/2024 00:00", datetime_format)
        if isinstance(datetime_input, datetime):
            current_datetime = datetime_input
        else:
            current_datetime = datetime.strptime(datetime_input, datetime_format)
        duration_hours = round(
            (current_datetime - reference_datetime).total_seconds() / 3600)
        return duration_hours
    except ValueError as e:
        logging.error(f"Date conversion error: {e}")
        raise


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


def validate_mission(mission):
    required_keys = ["_id", "startDate", "endDate", "soldierCount", "soldiersOnMission"]
    for key in required_keys:
        if key not in mission:
            raise ValueError(f"Mission {mission.get('_id', 'Unknown')} missing required data: {key}")
    datetime_to_hours(mission["startDate"])
    datetime_to_hours(mission["endDate"])


# def validate_soldier(soldier):
#     required_keys = ["personalNumber", "fullName", "pakal"]
#     for key in required_keys:
#         if key not in soldier:
#             raise ValueError(f"Soldier missing required data: {key}")

#     # Validate requestList
#     if "requestList" in soldier:
#         for request in soldier["requestList"]:
#             required_request_keys = ["requestType", "daysOffType", "startDate", "endDate"]
#             for req_key in required_request_keys:
#                 if req_key not in request:
#                     raise ValueError(f"Request in soldier {soldier['personalNumber']} missing required data: {req_key}")

# def validate_request_dates(requests):
#     for request in requests:
#         # Example validation: Ensure start_date is before end_date
#         if datetime.strptime(request.start_date, "%d/%m/%Y %H:%M") >= datetime.strptime(request.end_date, "%d/%m/%Y %H:%M"):
#             raise ValueError("Request start_date must be before end_date.")


def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error: {e}")
        raise


def getMissions(missions_data):
    missions = []
    for mission_data in missions_data:
        try:
            validate_mission(mission_data)
            mission = Mission(
                missionId=str(mission_data["_id"]),
                missionType=mission_data["missionType"],
                classId=int(mission_data["classId"]),
                startDate=mission_data["startDate"],
                endDate=mission_data["endDate"],
                soldierCount=int(mission_data["soldierCount"]),
                soldiersOnMission=mission_data.get("soldiersOnMission", [])
            )
            missions.append(mission)
        except Exception as e:
            logging.error(f"Failed to process mission:")
            return json.dumps({"error": "Failed to process mission."})

    return missions


def getSoldiers(soldiers_data):
    soldiers = []
    for soldier_data in soldiers_data:
        try:
            # Parse requests for each soldier
            requestsList = []
            if "requestList" in soldier_data:
                for request_data in soldier_data["requestList"]:
                    try:
                        request = Request(
                            requestType=request_data["requestType"],
                            daysOffType=request_data["daysOffType"],
                            start_date=request_data["startDate"],
                            end_date=request_data["endDate"]
                        )
                        requestsList.append(request)
                    except ValueError as e:
                        logging.error(
                            f"Error processing request for soldier {soldier_data.get('personalNumber', 'Unknown')}: {e}")

            # Initialize a Soldier object
            soldier = Soldier(
                personalNumber=int(soldier_data["personalNumber"]),
                fullName=str(soldier_data["fullName"]),
                classId=int(soldier_data['depClass']['classId']),
                className=str(soldier_data['depClass']["className"]),
                pakal=str(soldier_data["pakal"]),
                requestsList=requestsList
            )
            soldiers.append(soldier)
        except Exception as e:
            logging.error(f"Failed to process soldier {soldier_data.get('personalNumber', 'Unknown')}: {e}")
            return json.dumps({"error": "Failed to process soldier."})
    return soldiers

# def getSoldiers(soldiers_data):
#     soldiers = []
#     for soldier_data in soldiers_data:
#         try:
#             requestsList = parseRequests(soldier_data.get("requestList", []))
#             validate_request_dates(requestsList)   
#             soldier = Soldier(
#                 personalNumber=int(soldier_data["personalNumber"]),
#                 fullName=str(soldier_data["fullName"]),
#                 classId=int(soldier_data['depClass']['classId']),
#                 className=str(soldier_data['depClass']["className"]),
#                 pakal=str(soldier_data["pakal"]),
#                 requestsList=requestsList            )
#             validate_soldier(soldier)  # Ensure soldier is valid based on current missions
#             soldiers.append(soldier)
#         except Exception as e:
#             logging.error(f"Failed to process soldier {soldier_data.get('personalNumber', 'Unknown')}: {e}")
#     return soldiers


# def getMissions(missions_data):
#     missions = []
#     for mission_data in missions_data:
#         mission = Mission(
#             missionId=str(mission_data["_id"]),
#             missionType=mission_data["missionType"],
#             startDate=mission_data["startDate"],
#             endDate=mission_data["endDate"],
#             soldierCount=int(mission_data["soldierCount"]),
#             soldiersOnMission=mission_data.get("soldiersOnMission", [])
#         )
#         missions.append(mission)
#     return missions

# def getSoldiers(soldiers_data):
#     soldiers = []
#     for soldier_data in soldiers_data:
#         soldier = Soldier(
#             personalNumber=int(soldier_data["personalNumber"]),
#             fullName=str(soldier_data["fullName"]),
#             classId=int(soldier_data['depClass']['classId']),
#             className=str(soldier_data['depClass']["className"]),
#             pakal=str(soldier_data["pakal"]),
#             # Assuming requestList contains mission assignment info; adapt as necessary
#             )
#         soldiers.append(soldier)
#     return soldiers
