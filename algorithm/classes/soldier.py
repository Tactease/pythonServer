# from request import Request
from enum import Enum
from datetime import datetime
from .request import getRequest

class PAKAL(Enum):
    DRIVER = 1
    MAG = 2
    SNIPER = 3
    MATOL = 4
    NEGEV = 5
    KALA = 6
    METADOR = 7
    LAV = 8
    MEDIC = 9
    ROVAI = 10
    CHAIN_COMMANDER = 11
    
class daysoffType(Enum):
    BET=0,
    GIMEL=1,
    DALET=2
    
class Soldier:
    def __init__(self, personalNumber, fullName, classId, className, pakal, requestsList):
        self.personalNumber = personalNumber
        self.fullName = fullName
        self.classId = classId
        self.className = className
        self.pakal = pakal
        self.missionHour = 0
        self.requestsList = requestsList if requestsList is not None else []

    def __str__(self):
        return f"Soldier: {self.fullName} (ID: {self.personalNumber}, Class: {self.className}, Pakal: {self.pakal})"

    def addRequest(self, request):
        self.requestsList.append(request)

    def getRequests(self):
        return self.requestsList

    def getSpecificRequest(self, index):
        print(f"Fetching request at index {index} for soldier {self.fullName}")
        try:
            request = self.requestsList[index]
            print(f"Found request: {request}")
            return request
        except IndexError:
            print(f"No request found at index {index}")
            return None
    
    def has_conflicting_requests(self, start_buffer, end_buffer):
        print("in has_conflicting_requests")
        for request in self.requestsList:
            request_start = request.startDate
            request_end = request.endDate
            # Check for any overlap between the request time and the buffer time
            if request.status == 'Approved' and not (request_end <= start_buffer or request_start >= end_buffer):
                return True
        return False
    
        
        
    
