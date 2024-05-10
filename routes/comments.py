
from flask import Blueprint, jsonify, request

from database import get_connection, get_reader_connection
from routes.login import requires_token
from utils import codes, get_auth_token, get_body, in_json


comments_blueprint = Blueprint("comments_blueprint", __name__)

@comments_blueprint.route("/comments", methods=["GET", "POST"])
@requires_token
def comments():
    try:
        
        if request.method == "GET":
            
            comment_id = request.args.get("comment_id")

            if not comment_id:
                return jsonify({"error": "Missing required parameters: (comment_id)"}), codes.BAD_REQUEST
            
            connection = get_reader_connection()
            cursor = connection.cursor()

            cursor.execute("""SELECT * FROM get_comment(%s)""", [comment_id])
            comment = cursor.fetchone()

            cursor.close()
            connection.close()

            return jsonify({
                "comment": comment[0],
                "person_id": comment[1] 
            })


        if request.method == "POST":
            
            body = get_body()

            if not in_json(body, ["comment", "type"]):
                return jsonify({"error": "Missing required fields: (comment, type)"}), codes.BAD_REQUEST
            

            connection = get_connection()
            cursor = connection.cursor()

            if body["type"] == "event":
                if not in_json(body, ["event_id"]):
                    return jsonify({"error": "Missing required fields: (event_id)"}), codes.BAD_REQUEST
                
                cursor.execute("""CALL reply_event(%s, %s, %s)""", [body["comment"], body["event_id"], get_auth_token()["id"]])
                
            if body["type"] == "comment":
                if not in_json(body, ["comment_id"]):
                    return jsonify({"error": "Missing required fields: (comment_id)"}), codes.BAD_REQUEST
                
                cursor.execute("""CALL reply_comment(%s, %s, %s)""", [body["comment"], body["comment_id"], get_auth_token()["id"]])

            connection.commit()
            cursor.close()
            connection.close()

            return jsonify({"message": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR