from flask import Flask, request, jsonify
import os
from algorithm.generate_schedule.generate_schedule import generate_mission_schedule
from algorithm.add_mission.add_mission import add_multiple_missions_with_soldiers
from algorithm.errors.error_handler import bad_request_error, not_found_error, internal_server_error
from algorithm.update_schedule import change_soldier_upon_request_approved
import json
from algorithm.parse_functions import getMissions, getSoldiers


app = Flask(__name__)

@app.errorhandler(400)
def handle_bad_request_error(error):
    return bad_request_error(error)

@app.errorhandler(404)
def handle_not_found_error(error):
    return not_found_error(error)   

@app.errorhandler(500)
def handle_internal_server_error(error):
    return internal_server_error(error)

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    try:
        data = request.json
        missions_json_str = data['missions']
        soldiers_json_str = data['soldiers']
        schedule = generate_mission_schedule(missions_json_str, soldiers_json_str)
        return jsonify(schedule)
    except KeyError as e:
        return jsonify({"error": "Missing key in request", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


@app.route('/add_mission', methods=['POST'])
def add_mission():
    try:
        data = request.json
        schedule_json = data['schedule']
        new_mission_details = data['new_mission']
        soldiers_json_str = data['soldiers']
        updated_schedule = add_multiple_missions_with_soldiers(schedule_json, new_mission_details, soldiers_json_str)
        return jsonify(updated_schedule)
    except KeyError as e:
        return jsonify({"error": "Missing key in request", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    
    
@app.route('/change_soldier_upon_request_approved', methods=['POST'])
def change_soldier_upon_request_approved_route():
  try:
    data = request.json
    missions = data['missions']
    soldiers = data['soldiers']
    request_approved = data['request_approved']

    updated_schedule = change_soldier_upon_request_approved(missions, soldiers, request_approved)
    # Convert the updated schedule to JSON before returning
    # print(updated_schedule)
    return jsonify(updated_schedule)
  except KeyError as e:
    return jsonify({"error": "Missing key in request", "message": str(e)}), 400
  except Exception as e:
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)
    app.run(debug=True, host='0.0.0.0', port=port)
