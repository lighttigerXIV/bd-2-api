from flask import Blueprint, request, jsonify
from database import get_connection, get_reader_connection
from routes.login import requires_token
from utils import codes, get_auth_token, get_body, get_bool_arg, get_date_timestamp, get_timestamp_date, in_json
from random import randint

events_blueprint = Blueprint("event_blueprint", __name__)


@events_blueprint.route("/events", methods=["GET","POST", "PUT"])
@requires_token
def event():
    try:
        if request.method == "GET":
            
            id = request.args.get("id")
            show_reserved = get_bool_arg("show_reserved", False)
            search = request.args.get("search")

            if search is not None:
                
                connection = get_reader_connection()
                cursor = connection.cursor()

                cursor.execute("""SELECT * FROM search_events(%s)""", [search])
                results = cursor.fetchall()

                events = [{
                    "id": result_row[0],
                    "name": result_row[1],
                    "type": result_row[2],
                    "begin_date": get_timestamp_date(result_row[3]),
                    "end_date": get_timestamp_date(result_row[4])
                } for result_row in results]

                connection.close()
                cursor.close()

                return jsonify({"events": events})

            if show_reserved:
                connection = get_reader_connection()
                cursor = connection.cursor()

                cursor.execute("""SELECT * FROM get_reserved_events(%s)""", [get_auth_token()["id"]])
                results = cursor.fetchall()

                events = [{
                    "id": row[0],
                    "name": row[1],
                    "type": row[2],
                    "begin_date": get_timestamp_date(row[3]),
                    "end_date": get_timestamp_date(row[4]),     
                } for row in results]

                cursor.close()
                connection.close()

                return jsonify({"events": events})

            if id:

                connection = get_reader_connection()
                cursor = connection.cursor()

                cursor.execute("""SELECT * FROM get_event(%s)""", [id])
                results = cursor.fetchone()

                if not results:
                    return jsonify({"error": "Event not found"}), codes.BAD_REQUEST
                
                event = {
                    "name": results[0],
                    "type": results[1],
                    "price": results[2],
                    "address": results[3],
                    "begin_date":get_timestamp_date(results[4]),
                    "end_date":get_timestamp_date(results[5]),
                    "canceled": results[6],
                    "seats": results[7],
                    "begin_reservation_date": get_timestamp_date(results[8]),
                    "end_reservation_date": get_timestamp_date(results[9]),
                    "person_id": results[10]
                }
                
                return jsonify({"event": event})

            else:
                
                connection = get_reader_connection()
                cursor = connection.cursor()

                cursor.execute("""SELECT * FROM get_all_events()""")

                results = cursor.fetchall()
                events = []

                for result_row in results:
                    events.append({
                        "id": result_row[0],
                        "name": result_row[1],
                        "type": result_row[2],
                        "begin_date": get_timestamp_date(result_row[3]),
                        "end_date": get_timestamp_date(result_row[4])
                    })
                    
                return jsonify({"events": events})

        if request.method == "POST":

            body = get_body()

            if not in_json(body, ["name", "type", "price", "address", "begin_date", "end_date", "seats", "begin_reservation_date", "end_reservation_date"]):
                return jsonify({"error": "Missing required fields: (name, type, price, address, begin_date, end_date, seats, begin_reservation_date, end_reservation_date)"}), codes.BAD_REQUEST

            connection = get_connection()
            cursor = connection.cursor()

            random_isbn = str(randint(1_000_000_000, 9_999_999_999))

            begin_date_timestamp = get_date_timestamp(body["begin_date"])
            
            end_date_timestamp = get_date_timestamp(body["end_date"])
            
            begin_reservation_date_timestamp = get_date_timestamp(body["begin_reservation_date"])
            
            end_reservation_date_timestamp = get_date_timestamp(body["end_reservation_date"])

            cursor.execute("""CALL insert_event(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        [random_isbn, body["name"], body["type"], body["price"], body["address"], begin_date_timestamp, end_date_timestamp, body["seats"], begin_reservation_date_timestamp , end_reservation_date_timestamp , get_auth_token()["id"]])

            connection.commit()
            cursor.close()
            connection.close()

            return jsonify({"message": "ok"})
        
        if request.method == "PUT":

            body = get_body()

            if not in_json(body, ["id"]):
                return jsonify({"error": "Missing required fields: (id)"}), codes.BAD_REQUEST
            

            connection = get_reader_connection()
            cursor = connection.cursor()

            cursor.execute("""SELECT * FROM get_event(%s)""",[body["id"]])
            results = cursor.fetchone()

            if not results:
                return jsonify({"error": "Event not found"})
            
            
            event = {
                "name": results[0],
                "type": results[1],
                "price": results[2],
                "address": results[3],
                "begin_date": results[4],
                "end_date": results[5],
                "canceled": results[6],
                "seats": results[7],
                "begin_reservation_date": results[8],
                "end_reservation_date": results[9]
            }

            token = get_auth_token()

            if token["id"] != results[10] and not token["admin"]:
                return jsonify({"error": "Can't update another user event"}), codes.UNAUTHORIZED

            if event["canceled"]:
                return jsonify({"error": "Can't update canceled events"}), codes.BAD_REQUEST

            if in_json(body, ["name"]):
                event["name"] = body["name"]

            if in_json(body, ["type"]):
                event["type"] = body["type"]

            if in_json(body, ["price"]):
                event["price"] = body["price"]

            if in_json(body, ["address"]):
                event["address"] = body["address"]

            if in_json(body, ["begin_date"]):
                event["begin_date"] = get_date_timestamp(body["begin_date"])

            if in_json(body, ["end_date"]):
                event["end_date"] = get_date_timestamp(body["end_date"])

            if in_json(body, ["canceled"]):
                event["canceled"] = body["canceled"]

            if in_json(body, ["seats"]):
                event["seats"] = body["seats"]

            if in_json(body, ["begin_reservation_date"]):
                event["begin_reservation_date"] = get_date_timestamp(body["begin_reservation_date"])

            if in_json(body, ["end_reservation_date"]):
                event["end_reservation_date"] = get_date_timestamp(body["end_reservation_date"])

            cursor.close()
            connection.close()

            connection = get_connection()
            cursor = connection.cursor()

            #return jsonify({"message": event})

            cursor.execute("""CALL update_event(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", [
                body["id"],
                event["name"],
                event["type"],
                event["price"],
                event["address"],
                event["begin_date"],
                event["end_date"],
                event["canceled"],
                event["seats"],
                event["begin_reservation_date"],
                event["end_reservation_date"],
            ])

            connection.commit()
            cursor.close()
            connection.close()

            return jsonify({"message": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR


@events_blueprint.route("/cancel-event", methods=["PUT"])
@requires_token
def cancel_event():
    try:

        body = get_body()

        if not in_json(body, ["id"]):
            return jsonify({"error": "Missing required fields: (id)"}), codes.BAD_REQUEST
        
        connection = get_reader_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT * FROM get_event(%s)""",[body["id"]])
        result = cursor.fetchone()

        if result[10] != get_auth_token()["id"] and not get_auth_token()["admin"]:
            return jsonify({"error": "Can't cancel another user event"}), codes.UNAUTHORIZED
        
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""CALL cancel_event(%s)""", [body["id"]])

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR