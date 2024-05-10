from flask import Blueprint, jsonify, request

from database import get_connection
from routes.login import requires_token
from utils import codes, get_auth_token, get_body, in_json


subscriptions_blueprint = Blueprint('subscriptions_blueprint', __name__)


@subscriptions_blueprint.route('/subscriptions', methods=['GET', 'POST', 'DELETE'])
@requires_token
def subscriptions():
    try:
        if request.method == "POST":
            
            body = get_body()

            if not in_json(body, ["event_id"]):
                return jsonify({"error": "Missing required fields: (event_id)"}), codes.BAD_REQUEST

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""CALL subscribe_event(%s, %s)""", [body["event_id"], get_auth_token()["id"]])
            
            connection.commit()
            cursor.close()
            connection.close()

            return jsonify({"message": "ok"})
        
        if request.method == "DELETE":
            
            event_id = request.args.get("event_id")

            if not event_id:
                return jsonify({"error": "Missing required parameters: (event_id)"}), codes.BAD_REQUEST
            
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""CALL unsubscribe_event(%s, %s)""", [event_id, get_auth_token()["id"]])

            connection.commit()
            cursor.close()
            connection.close()

            return jsonify({"message": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR