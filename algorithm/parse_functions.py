import logging
from datetime import datetime
from .classes.mission import Mission
from .classes.request import Request
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
        raise e


def parse_datetime(date_str):
    return datetime.strptime(date_str, '%d/%m/%Y %H:%M')


def validate_mission(mission):
    required_keys = ["_id", "startDate", "endDate", "soldierCount", "soldiersOnMission"]
    for key in required_keys:
        if key not in mission:
            raise ValueError(f"Mission {mission.get('_id', 'Unknown')} missing required data: {key}")
    datetime_to_hours(mission["startDate"])
    datetime_to_hours(mission["endDate"])


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
            raise e
    return missions


import logging

def getSoldiers(soldiers_data):
    soldiers = []
    for soldier_data in soldiers_data:
        if isinstance(soldier_data, dict) and "personalNumber" in soldier_data:
            try:
                requestsList = []
                # Parse requests for each soldier
                if "requestList" in soldier_data:
                    for request_data in soldier_data["requestList"]:
                        try:
                            # Validate that all required keys are present
                            required_request_keys = ["requestType", "startDate", "endDate", "status"]
                            if not all(key in request_data for key in required_request_keys):
                                raise ValueError(f"Missing required request keys in {request_data}")
                            # Create a Request object
                            request = Request(
                                requestType=request_data["requestType"],
                                startDate=request_data["startDate"],
                                endDate=request_data["endDate"],
                                status=request_data["status"]
                            )
                            requestsList.append(request)
                        except (KeyError, ValueError) as e:
                            logging.error(f"Error processing request for soldier {soldier_data.get('personalNumber', 'Unknown')}: {e}")
                # Validate soldier data
                required_soldier_keys = ["personalNumber", "fullName", "depClass", "pakal"]
                if not all(key in soldier_data for key in required_soldier_keys):
                    raise ValueError(f"Missing required soldier keys in {soldier_data}")
                # Initialize a Soldier object
                soldier = Soldier(
                    personalNumber=int(soldier_data["personalNumber"]),
                    fullName=str(soldier_data["fullName"]),
                    classId=int(soldier_data["depClass"]["classId"]),
                    className=str(soldier_data["depClass"]["className"]),
                    pakal=str(soldier_data["pakal"]),
                    requestsList=requestsList
                )
                soldiers.append(soldier)
            except Exception as e:
                logging.error(f"Failed to process soldier {soldier_data.get('personalNumber', 'Unknown')}: {e}")
        else:
            logging.warning(f"Unexpected data found in soldiers data: {soldier_data}")

    return soldiers



# def getRequest(request_data):
#     try:
#         requestApproval = Request(
#         requestType=str(request_data["requestType"]),
#         daysOffType=str(request_data["daysOffType"]),
#         start_date=str(request_data["startDate"]),
#         end_date=str(request_data["endDate"]),
#         requestIndex=int(request_data["soldiersOnMission"]),
#         )
#     except Exception as e:
#         logging.error(f"Failed to process request:")
#         raise e
#     print(requestApproval.requestType)
#     return requestApproval