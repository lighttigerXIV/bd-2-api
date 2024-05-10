from datetime import datetime
from flask import request
import jwt
import settings

def get_body():
    """Returns the body in the request"""
    return request.json

def get_auth_header():
    """
    Returns the token inside the Authorization header.
    """
    return request.headers.get("Authorization")

def get_bool_arg(arg, default):
    
    argument = request.args.get(arg)
    
    if argument is None:
        return default
    
    if argument.lower() == "true":
        return True
    
    if argument.lower() == "false":
        return False

    return default

def get_auth_token():
    """Returns the decoded token"""
    header = get_auth_header()
    header_split = header.split(' ')

    if len(header_split) < 2:
        return None
    
    if header_split[0] != "Bearer":
        return None

    token = jwt.decode(header_split[1].encode(), settings.TOKENS_KEY, algorithms=["HS256"])

    return token


def in_json(json, fields) -> bool:

    for field in fields:
        if not field in json:
            return False

    return True


class codes:
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    API_ERROR = 500


def get_date_timestamp(date):
    return int(datetime.strptime(date, "%d-%m-%Y %H:%M").timestamp())

def get_timestamp_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M")