import psycopg2
import settings


def get_connection():
    return psycopg2.connect(settings.DATABASE_URL)

def get_reader_connection():
    return psycopg2.connect(settings.DATABASE_READER_URL)

def get_cursor():
    return get_connection().cursor()