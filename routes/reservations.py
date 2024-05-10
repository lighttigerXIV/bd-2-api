
from flask import Blueprint, jsonify, request

from database import get_connection
from routes.login import requires_token
from utils import codes, get_auth_token, get_body, in_json


reservations_blueprint = Blueprint("reservations_blueprint", __name__)

@reservations_blueprint.route("/reservations", methods=["POST"])
@requires_token
def reservations():
    try:
        if request.method == "POST":
            
            body = get_body()
            
            if not in_json(body, ["event_id"]):
                return jsonify({"error": "Missing required fields: (event_id)"}), codes.BAD_REQUEST

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""CALL reserve_event(%s, %s)""", [body["event_id"], get_auth_token()["id"]])
            connection.commit()
            cursor.close()
            connection.close()

            return jsonify({"message": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR
    

@reservations_blueprint.route("/cancel-reservation", methods=["DELETE"])
@requires_token
def cancel_reservation():
    try:
        
        event_id = request.args.get("event_id")

        if event_id is None:
            return jsonify({"error": "Missing required parameters: (event_id)"}), codes.BAD_REQUEST
        
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""CALL unreserve_event(%s, %s)""", [event_id, get_auth_token()["id"]])

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR