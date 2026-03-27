# I have chosen to use pytest because it gives simple assert syntax, 
# clear failure messages and automatically exits with a non-zero code 
# when tests fail, which align with the assignment requirements.

import os
import time
import requests
import pytest

NGINX_HOST = os.getenv("NGINX_HOST")
HTML_PORT = os.getenv("SERVER_HTML_PORT")
ERROR_PORT = os.getenv("SERVER_ERROR_PORT")


@pytest.fixture(scope="session", autouse=True)
def nginx_health_check():
    """
    Waits for the Nginx server to become reachable before any tests run.

    The fixture retries sending an HTTP request to the HTML port for a 
    limited time.If the server does not respond successfully, the test 
    session fails.
    """
    url = f"http://{NGINX_HOST}:{HTML_PORT}/"
    for _ in range(15):
        try:
            requests.get(url, timeout=2)
            break
        except Exception:
            time.sleep(0.5)
    else:
        pytest.fail(f"Nginx not reachable at {url}")


def test_html_port():
    """
    Verifies that Nginx server returns HTML content on HTML port.
    """
    r = requests.get(f"http://{NGINX_HOST}:{HTML_PORT}/")
    assert r.status_code == 200
    assert "Service is running." in r.text


def test_error_port():
    """
    Verifies that Nginx server returns an HTTP error response on error 
    port.
    """
    r = requests.get(f"http://{NGINX_HOST}:{ERROR_PORT}/")
    assert not r.ok