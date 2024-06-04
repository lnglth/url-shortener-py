import datetime
import urllib.parse

import validators
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from .utils import connect_database, generate_short_url

BASE_URL = "http://localhost:8000/"
app = FastAPI()


@app.get("/")
def homepage():
    return "Welcome to the URL shortener API written in Python!"


@app.post("/shorten")
def shorten_url(url: str, expired_date: int = 30):
    """Shorten a URL to a shorter one

    Attributes:
        url(str): The URL to be shortened
        expired_date(int): The number of days the shortened URL will be valid

    Returns:
        dict: The shortened URL
    """

    # Preprocess URL
    url = urllib.parse.unquote(url)
    if not validators.url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")

    conn = connect_database()
    cur = conn.cursor()

    # TODO: Can use some cache before access to database to gain more speed
    # Check if the URL already exists in database
    cur.execute(
        "SELECT short_url, created_at, expired_at, click_count FROM url WHERE original_url = %s",
        (url,),
    )
    query = cur.fetchone()
    if query:
        return {
            "short_url": f"{BASE_URL}{query[0]}",
            "created_at": query[1],
            "expired_at": query[2],
            "click_count": query[3],
        }

    # Otherwise, generate a new short URL
    short_url = generate_short_url()
    while True:
        cur.execute("SELECT short_url FROM url WHERE short_url = %s", (short_url,))
        if not cur.fetchone():
            break
        short_url = generate_short_url()

    # Insert the new URL into the database
    cur.execute(
        "INSERT INTO url (original_url, short_url, expired_at, created_at) VALUES (%s, %s, %s, %s)",
        (
            url,
            short_url,
            datetime.now() + timedelta(days=expired_date),
            datetime.now(),
        ),
    )

    # Commit and close DB
    conn.commit()
    cur.close()
    conn.close()

    return {"short_url": f"{BASE_URL}{short_url}"}


@app.get("/{short_url}")
def redirect_url(short_url: str):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute(
        "SELECT original_url, click_count FROM url WHERE short_url = %s AND expired_at > %s",
        (short_url, datetime.now().date()),
    )

    query = cur.fetchone()
    if not query:
        raise HTTPException(status_code=404, detail="URL not found")
    else:
        # Increment click count
        cur.execute(
            "UPDATE url (click_count) VALUES (%s) WHERE short_url = %s",
            (query[1] + 1, short_url),
        )
        original_url = query[0]
        click_count = query[1] + 1

    headers = {
        "click_count": str(click_count),
    }

    # Commit and close DB
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse(url=original_url, headers=headers)
