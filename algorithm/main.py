from cpAlgorithm import scheduleAlg

mDict = [{"missionType":"PATROL_BY_FOOT","startDate":"12/02/2024 14:00","endDate":"12/02/2024 16:00","soldierCount":4,"soldiersOnMission":[],"_id":"65d88864081fe1eb0b2c8b4f","__v":0}]
sDictList = [{"_id":"65cfa5a32d24db0d430f77c2","personalNumber":1234567,"fullName":"Ran Lachmi","pakal":"SNIPER","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b52"}},
             {"_id":"65cfa5a32d24db0d430f77c3","personalNumber":8765421,"fullName":"Eido Peretz","pakal":"MAG","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b53"}},
             {"_id":"65cfa5a32d24db0d430f77c4","personalNumber":1122334,"fullName":"Amit Levi","pakal":"ROVAI","requestList":[],"depClass":{"classId":40, "className":"Haruvit","_id":"65d88864081fe1eb0b2c8b54"}},
             {"_id":"65cfa5a32d24db0d430f77c5","personalNumber":1233215,"fullName":"Idan Itah","pakal":"KALA","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b55"}},
             {"_id":"65cfa5a32d24db0d430f77c6","personalNumber":9879654,"fullName":"Naim Ganem","pakal":"METADOR","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b56"}},
             {"_id":"65cfa5a32d24db0d430f77c7","personalNumber":8256412,"fullName":"Adi Levi","pakal":"MEDIC","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b57"}},
             {"_id":"65cfa5a32d24db0d430f77c8","personalNumber":6546546,"fullName":"Moran Sinai","pakal":"SNIPER","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b58"}},
             {"_id":"65cfa5a32d24db0d430f77c9","personalNumber":9857656,"fullName":"Irit Cohen","pakal":"MAG","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b59"}},
             {"_id":"65cfa5a32d24db0d430f77ca","personalNumber":1589874,"fullName":"Alice Peretz","pakal":"KALA","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b5a"}},
             {"_id":"65cfa5a32d24db0d430f77cb","personalNumber":6589711,"fullName":"Guy Yaffe","pakal":"MEDIC","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b5b"}},
             {"_id":"65cfa5a32d24db0d430f77cc","personalNumber":5555555,"fullName":"Noy richman","pakal":"ROVAI","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b5c"}},
             {"_id":"65cfa5a32d24db0d430f77cd","personalNumber":1232323,"fullName":"Noam Sinay","pakal":"CHAIN COMMANDER","requestList":[],"depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b5d"}},
             {"_id":"65cfa5a32d24db0d430f77ce","personalNumber":1111111,"fullName":"Yasmin Adler","pakal":"COMMANDER","depClass":{"classId":40,"className":"Haruvit","_id":"65d88864081fe1eb0b2c8b5e"}}]

res =scheduleAlg(mDict, sDictList)
print(res)