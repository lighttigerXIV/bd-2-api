from flask import Blueprint, request, jsonify
from database import get_connection
from utils import codes, get_auth_token, get_body, in_json
from .login import requires_token

person_blueprint = Blueprint("person_blueprint", __name__)


@person_blueprint.route("/register", methods=["POST"])
def register():
    try:
        body = get_body()

        if not in_json(body, ["name", "username", "email", "password"]):
            return jsonify({"error": "Missing required fields: (name, username, email, password)"}), codes.BAD_REQUEST

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""CALL register_user(%s, %s, %s, %s)""",
                       [body["name"], body["username"], body["password"], body["email"]])

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR
    

@person_blueprint.route("/ban", methods=["PUT"])
@requires_token
def ban():
    try:
        
        if not get_auth_token()["admin"]:
            return jsonify({"error": "Only admins can ban people"}), codes.UNAUTHORIZED
        
        body = get_body()

        if not body["person_id"]:
            return jsonify({"error": "Missing required fields: (person_id)"}), codes.BAD_REQUEST

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""CALL ban_person(%s)""", [body["person_id"]])

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR