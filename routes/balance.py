from flask import Blueprint, jsonify, request

from database import get_connection, get_reader_connection
from routes.login import requires_token
from utils import codes, get_auth_token, get_body, in_json


balance_blueprint = Blueprint("balance_blueprint", __name__)

@balance_blueprint.route("/balance", methods=["GET", "PUT"])
@requires_token
def balance():
    try:
        
        if request.method == "GET":
            
            connection = get_reader_connection()
            cursor = connection.cursor()

            cursor.execute("""SELECT * FROM get_balance(%s)""", [get_auth_token()["id"]])
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "User not found"}), codes.BAD_REQUEST
            
            return jsonify({"balance": result[0]})

        
        if request.method == "PUT":
            body = get_body()

            if not in_json(body, ["amount", "action"]):
                return jsonify({"error": "Missing required fields: (amount, action)"}), codes.BAD_REQUEST
            
            if body["amount"] <= 0:
                return jsonify({"error": "Can't charge a negative amount"}), codes.BAD_REQUEST
            
            if body["action"] not in ["charge", "reduce"]:
                return jsonify({"error": "Invalid action"}), codes.BAD_REQUEST


                
            connection = get_connection()
            cursor = connection.cursor()

            if body["action"] == "charge":
                cursor.execute("""CALL charge_balance(%s, %s)""", [get_auth_token()["id"], body["amount"]])

            else:
                cursor.execute("""CALL reduce_balance(%s, %s)""", [get_auth_token()["id"], body["amount"]])

            connection.commit()
            cursor.close()
            connection.close()
            
            connection = get_connection()

            return jsonify({"message": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR