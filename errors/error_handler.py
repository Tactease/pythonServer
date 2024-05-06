from flask import jsonify

def bad_request_error(error):
    return jsonify({"error": "Bad Request", "message": str(error)}), 400

def not_found_error(error):
    return jsonify({"error": "Not Found", "message": str(error)}), 500

def internal_server_error(error):
    return jsonify({"error": "Internal Server Error", "message": str(error)}), 500
