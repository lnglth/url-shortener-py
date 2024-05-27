import os
import secrets
import string

import psycopg2


def generate_short_url(length: int = 6) -> str:
    """Use to generate a short URL with a predefined length"""
    characters = string.ascii_letters + string.digits
    short_url = "".join(secrets.choice(characters) for _ in range(length))
    return short_url


def connect_database():
    # try:
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    # except Exception:
    # raise HTTPException(status_code=500, detail="Database connection failed")
    return conn
