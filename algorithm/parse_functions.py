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
                        raise e

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
            raise e
    return soldiers
