from datetime import datetime


class Request:
    def __init__(self, requestType, daysOffType, start_date, end_date):
        datetime_format = "%d/%m/%Y %H:%M"  # Updated format to include time
        self.requestType = requestType
        self.daysOffType = daysOffType
        self.start_date = datetime.strptime(start_date, datetime_format)
        self.end_date = datetime.strptime(end_date, datetime_format)


class MedicalRequest(Request):
    def __init__(self, requestType, daysOffType, start_date, end_date, file, fileName):
        super().__init__(requestType, daysOffType, start_date, end_date)
        self.file = file  # This could be a path to the file
        self.fileName = fileName


class PersonalRequest(Request):
    def __init__(self, requestType, daysOffType, start_date, end_date, note):
        super().__init__(requestType, daysOffType, start_date, end_date)
        self.note = note

    def getNote(self):
        return self.note
