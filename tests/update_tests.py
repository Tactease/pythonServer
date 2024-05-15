# import unittest
# import json
# import requests
# from algorithm.generate_schedule.update_schedule import change_soldier_upon_request_approved

# class TestUpdateSchedule(unittest.TestCase):
#     def setUp(self):
#         self.mock_missions = [
#             {
#                 "missionId": '65f2de405148ef9ba362d1fa',
#                 "missionType": 'GUARD',
#                 "startDate": '2024-02-12T06:00:00',
#                 "endDate": '2024-02-12T10:00:00',
#                 "soldierCount": 2,
#                 "soldiersOnMission": [1234, 5678],
#             },
#             {
#                 "missionId": '65f2d33a68583409daedeb0a',
#                 "missionType": 'GUARD',
#                 "startDate": '2024-02-12T14:00:00',
#                 "endDate": '2024-02-12T18:00:00',
#                 "soldierCount": 3,
#                 "soldiersOnMission": [11, 22, 33, 44],
#             }
#         ]

#         self.mock_soldiers = {
#             "12345": {
#                 "_id": "65cfa5a32d24db0d430f77c2",
#                 "personalNumber": 12345,
#                 "fullName": "Ran Lachmi",
#                 "pakal": "SNIPER",
#                 "requestList": [
#                     {
#                         "requestType": "MEDICAL_REQUEST",
#                         "daysOffType": "SICK_LEAVE",
#                         "startDate": "2024-02-12T14:00:00",
#                         "endDate": "2024-02-12T16:00:00",
#                         "note": "I'm sick",
#                         "fileName": "sick_note.jpg",
#                         "status": "Approved"
#                     },
#                     {
#                         "requestType": "PERSONAL_REQUEST",
#                         "daysOffType": "VACATION",
#                         "startDate": "2024-02-12T18:00:00",
#                         "endDate": "2024-02-12T23:00:00",
#                         "note": "my sister gettin married.",
#                         "fileName": "invitation.png",
#                         "status": "Pending"
#                     }
#                 ],
#                 "depClass": {
#                     "classId": 40,
#                     "className": "Haruvit",
#                     "password": "$2b$10$6Srl1GrnmaiZQUsfNaJj1uYYw5MkytECqbqrLydv9syyPGYNrfDzG"
#                 }
#             },
#             "6546546": {
#                 "_id": "65cfa5a32d24db0d430f77c8",
#                 "personalNumber": 6546546,
#                 "fullName": "Moran Sinai",
#                 "pakal": "SNIPER",
#                 "requestList": [
#                     {
#                         "requestType": "UPDATED",
#                         "daysOffType": "UPDATED",
#                         "startDate": "2024-02-22T14:00:00",
#                         "endDate": "2024-02-22T16:00:00",
#                         "note": "kakapopo",
#                         "fileName": "sick_note.jpg"
#                     }
#                 ],
#                 "depClass": {
#                     "classId": 40,
#                     "className": "Haruvit"
#                 }
#             }
#         }

#         self.request_approved = {
#             "personalNumber": "12345",
#             "requestIndex": 0,
#             "startDate": "2024-02-12T08:00:00",
#             "endDate": "2024-02-13T17:00:00"
#         }

#         self.flask_url = "http://localhost:5000/change_soldier_upon_request_approved"
#         self.node_url = "http://localhost:3000/change_soldier_upon_request_approved"

#     def test_change_soldier_upon_request_approved(self):
#         flask_response = requests.post(self.flask_url, json={
#             "schedule_json_str": json.dumps(self.mock_missions),
#             "soldiers": json.dumps(self.mock_soldiers),  # Correct key name
#             "request_approved": self.request_approved
#         })
#         # Assert Flask server response
#         self.assertEqual(flask_response.status_code, 200)
#         updated_schedule_flask = flask_response.json()

#         # Send request to Node.js server
#         node_response = requests.post(self.node_url, json={
#             "schedule_json_str": json.dumps(self.mock_missions),
#             "soldiers": json.dumps(self.mock_soldiers),  # Correct key name
#             "request_approved": self.request_approved
#         })
#         # Assert Node.js server response
#         self.assertEqual(node_response.status_code, 200)
#         updated_schedule_node = node_response.json()

#         # Add assertions to verify the correctness of the updated_schedule
#         # Assert updated_schedule_flask and updated_schedule_node are equal
#         self.assertEqual(updated_schedule_flask, updated_schedule_node)

#         # Add additional assertions based on expected changes in the updated_schedule
#         # For example, check if the soldier has been replaced as expected
        
# if __name__ == "__main__":
#     unittest.main()

import json

# Your dictionary data
data = {
    "missions": [
        {
            "_id": "662cd7c79391db315e2ae38a",
            "classId": 40,
            "missionType": "MISSION",
            "startDate": "28/04/2024 17:15",
            "endDate": "28/04/2024 23:15",
            "soldierCount": 5,
            "soldiersOnMission": [8765421, 6589711],
            "__v": 0
        },
        {
            "_id": "662cd7c79391db315e2ae38c",
            "classId": 40,
            "missionType": "WATCH",
            "startDate": "28/04/2024 12:16",
            "endDate": "28/04/2024 16:16",
            "soldierCount": 2,
            "soldiersOnMission": [],
            "__v": 0
        },
        {
            "_id": "662cd9de9391db315e2ae3ca",
            "classId": 40,
            "missionType": "WATCH",
            "startDate": "28/04/2024 17:00",
            "endDate": "28/04/2024 21:55",
            "soldierCount": 2,
            "soldiersOnMission": [],
            "__v": 0
        }
    ],
    "soldiers": {
        "12345": {
            "_id": "65cfa5a32d24db0d430f77c2",
            "personalNumber": 12345,
            "fullName": "Ran Lachmi",
            "pakal": "SNIPER",
            "requestList": [
                {
                    "requestType": "MEDICAL_REQUEST",
                    "daysOffType": "SICK_LEAVE",
                    "startDate": "2024-02-12T14:00:00",
                    "endDate": "2024-02-12T16:00:00",
                    "note": "I'm sick",
                    "fileName": "sick_note.jpg",
                    "status": "Approved"
                },
                {
                    "requestType": "PERSONAL_REQUEST",
                    "daysOffType": "VACATION",
                    "startDate": "2024-02-12T18:00:00",
                    "endDate": "2024-02-12T23:00:00",
                    "note": "my sister gettin married.",
                    "fileName": "invitation.png",
                    "status": "Pending"
                }
            ],
            "depClass": {
                "classId": 40,
                "className": "Haruvit",
                "password": "$2b$10$6Srl1GrnmaiZQUsfNaJj1uYYw5MkytECqbqrLydv9syyPGYNrfDzG"
            }
        },
        "6546546": {
            "_id": "65cfa5a32d24db0d430f77c8",
            "personalNumber": 6546546,
            "fullName": "Moran Sinai",
            "pakal": "SNIPER",
            "requestList": [
                {
                    "requestType": "UPDATED",
                    "daysOffType": "UPDATED",
                    "startDate": "2024-02-22T14:00:00",
                    "endDate": "2024-02-22T16:00:00",
                    "note": "kakapopo",
                    "fileName": "sick_note.jpg"
                }
            ],
            "depClass": {
                "classId": 40,
                "className": "Haruvit"
            }
        }
    },
    "request_approved": {
        "personalNumber": "12345",
        "requestIndex": 0
    }
}

# Convert the dictionary to a JSON string
json_data = json.dumps(data)

# Print the JSON string
print(json_data)
