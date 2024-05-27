from fastapi.testclient import TestClient

from url_shortener.api import app

client = TestClient(app)


def test_shorten_url():
    """
    Test that a new URL can be shortened successfully.
    """
    params = {
        "url": "https://news.ycombinator.com/news?p=1",
    }
    response = client.post(url="/shorten", params=params)
    assert response.status_code == 200

    assert "short_url" in response.json()

    short_url = response.json()["short_url"]
    assert len(short_url) < len(params["url"])


def test_redirect_to_original_url():
    """
    Test that a short URL redirects to the original URL.
    """

    params = {
        "url": "https://news.ycombinator.com/news?p=2",
    }

    response = client.post("/shorten", params=params)
    short_url = response.json()["short_url"]

    response = client.get(f"/{short_url.split('/')[-1]}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == params["url"]


def test_non_existent_short_url():
    """
    Test that a non-existent short URL returns a 404 error.
    """
    short_url = "http://localhost:8000/invalid"
    response = client.get(f"/{short_url.split('/')[-1]}", follow_redirects=False)
    assert response.status_code == 404


def test_url_validation():
    """
    Test that invalid URLs are rejected when shortening.
    """
    params = {
        "url": "invalid_url",
    }
    response = client.post("/shorten", params=params)
    assert response.status_code == 400


def test_click_count():
    """
    Test that the click count is incremented correctly.
    """
    params = {
        "url": "https://www.google.com/search?q=url+shortener&oq=url+shortener",
    }

    client.post("/shorten", params=params)

    response = client.post("/shorten", params=params)
    short_url = response.json()["short_url"]

    click_count_initial = response.json()["click_count"] - 1

    # Simulate a few clicks on the short URL
    for _ in range(5):
        response = client.get(f"/{short_url.split('/')[-1]}", follow_redirects=False)
        click_count_final = int(response.headers["click_count"])

    # Check the click count
    assert click_count_final == click_count_initial + 5
