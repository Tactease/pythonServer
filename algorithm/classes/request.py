from datetime import datetime


class Request:
    def __init__(self, requestType, startDate, endDate, status):
        datetime_format = "%d/%m/%Y %H:%M"  # Updated format to include time
        self.requestType = requestType
        self.startDate = datetime.strptime(startDate, datetime_format)
        self.endDate = datetime.strptime(endDate, datetime_format)
        self.status = status


class MedicalRequest(Request):
    def __init__(
        self, requestType, startDate, endDate, file, fileName, status
    ):
        super().__init__(requestType, startDate, endDate, status)
        self.file = file  # This could be a path to the file
        self.fileName = fileName


class PersonalRequest(Request):
    def __init__(self, requestType, startDate, endDate, note, status):
        super().__init__(requestType, startDate, endDate, status)
        self.note = note

    def getNote(self):
        return self.note


def getRequest(request_data):
    request_type = request_data.get("requestType", "UNKNOWN")
    startDate = request_data.get("startDate")
    endDate = request_data.get("endDate")
    note = request_data.get("note")
    status = request_data.get("status")

    if request_type == "MEDICAL_REQUEST":
        return MedicalRequest(request_type, startDate, endDate, note, status)
    elif request_type == "PERSONAL_REQUEST":
        return PersonalRequest(request_type, startDate, endDate, note, status)
    else:
        raise ValueError("Invalid request type")
