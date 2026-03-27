# using alpine because it keeps the image small
FROM python:3.12-alpine

WORKDIR /tests

RUN pip install --no-cache-dir requests==2.31.0 pytest==8.3.3

COPY test_nginx.py .

CMD ["pytest", "test_nginx.py", "-v"]

