# Dockerized Nginx with Automated Tests

Docker Compose stack that runs Nginx and a pytest-based test container. Nginx serves a static page over HTTP/HTTPS(each on a different port) and exposes an additional port that intentionally always returns an error response.

## Description

This project is designed to demonstrate:

- Docker image builds (Nginx + test runner)
- Docker Compose orchestration with service dependencies
- Automated validation of Nginx availability and HTTP/HTTPS responses using `pytest` + `requests`
- Nginx configuration supporting HTTP, HTTPS with a self-signed certificate, and an error endpoint 

## Getting Started

### Dependencies

- Docker (Engine) installed and running
- Docker Compose v2 available through the command `docker compose`

### Setup

Clone the GitHub repository and navigate to the poroject directory.


### Running the Tests

Build and run the docker compose stack:

```bash
docker compose up --build
```

Notes:

- Tests run automatically inside the `test` container.
- **Exit code 0** = pass, **non-zero** = fail.

## Usage:

With the default `.env` values:

- **HTTP HTML**: `http://localhost:8080/`
  - Expected: `200 OK` and HTML containing `Service is running.`
- **HTTP error**: `http://localhost:9090/`
  - Expected: `500` (or generally any HTTP error response)
- **HTTPS HTML (self-signed)**: `https://localhost:8443/`
  - Expected: `200 OK` and HTML containing `Service is running.`(your browser will warn you about the untrusted certificate)

## Continuous Integration:

GitHub Actions workflow: `.github/workflows/run_tests.yml`

On every push, the CI pipeline executes the docker compose and pytest-based tests to validate Nginx behavior.

