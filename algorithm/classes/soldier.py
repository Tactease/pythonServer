# from request import Request
from enum import Enum

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
    def __init__(self, personalNumber, fullName, classId, className, pakal, requestsList=None):
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

    def getSpecificRequest(self, request_id):
        for request in self.requestsList:
            if request.request_id == request_id:
                return request
        return None
    
