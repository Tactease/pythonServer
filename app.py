
from flask import Flask, request, jsonify
import os
from algorithm.generate_schedule.generate_schedule import generate_mission_schedule
from algorithm.add_mission.add_mission import add_new_mission_with_soldiers


app = Flask(__name__)


@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({"error": "Bad Request", "message": str(error)}), 400


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found", "message": str(error)}), 500


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error", "message": str(error)}), 500


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
        updated_schedule = add_new_mission_with_soldiers(schedule_json, new_mission_details, soldiers_json_str)
        return jsonify(updated_schedule)
    except KeyError as e:
        return jsonify({"error": "Missing key in request", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use PORT environment variable if available, otherwise default to 5000
    app.run(debug=True, port=port)
