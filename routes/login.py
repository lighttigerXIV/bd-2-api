from flask import Blueprint, request, jsonify
from database import get_connection, get_reader_connection
from utils import get_auth_header, get_auth_token, get_body, in_json, codes
import jwt
import settings
import datetime
from functools import wraps

login_blueprint = Blueprint("login_blueprint", __name__)


def requires_token(f):
    """
    This function is a wrapper for the Authorization.
    It gets the `Authorization` header and reads the token. If the token is not sent, valid or has expired
    it returns a error
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        if not get_auth_header():
            return jsonify({"error": "Missing authorization token"}), codes.BAD_REQUEST

        token = get_auth_token()

        if not token:
            return jsonify({"error": "Wrong token type. Must send 'Bearer {token}'"})

        expire_date = datetime.datetime.fromtimestamp(
            token["expire_date"]).timestamp()
        current_date = datetime.datetime.now().timestamp()

        if expire_date < current_date:
            return jsonify({"error": "Token has expired"}), codes.BAD_REQUEST

        connection = get_reader_connection()
        cursor = connection.cursor()

        cursor.execute("""SELECT * FROM get_user(%s)""",
                       [get_auth_token()["email"]])
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "User doesn't exist or it's banned"})

        connection.close()
        cursor.close()

        return f(*args, **kwargs)

    return decorator


@login_blueprint.route("/login", methods=["POST"])
def login():
    try:
        if request.method == "POST":

            body = get_body()

            if not in_json(body, ["email", "password"]):
                return jsonify({"error": "Missing required fields: (email, password)"}), codes.BAD_REQUEST

            connection = get_reader_connection()
            cursor = connection.cursor()

            cursor.execute("""SELECT * FROM login_user(%s, %s)""", [body["email"], body["password"]])
            result = cursor.fetchone()

            if result is None:
                return jsonify({"error": "Wrong credentials or user is banned"})              
            
            id, is_admin = result

            token = jwt.encode({
                "id": id,
                "email": body["email"],
                "admin": is_admin,
                "expire_date": (datetime.datetime.now() + datetime.timedelta(days=7)).timestamp()
            }, settings.TOKENS_KEY).decode()

            connection.close()
            cursor.close()

            return jsonify({"token": token})
    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR


@login_blueprint.route("/token-login", methods=["POST"])
@requires_token
def token_login():
    """
    Tries to login with the required token. 
    If it's still not expired it will return a renewed token with another expire date
    """

    try:
        token = get_auth_token()

        renewed_token = jwt.encode({
            "id": token["id"],
            "email": token["email"],
            "admin": token["admin"],
            "expire_date": (datetime.datetime.now() + datetime.timedelta(days=7)).timestamp()
        }, settings.TOKENS_KEY).decode()

        return jsonify({"token": renewed_token})

    except Exception as e:
        return jsonify({"error": str(e)}), codes.API_ERROR
