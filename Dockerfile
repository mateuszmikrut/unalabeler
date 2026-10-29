FROM cgr.dev/chainguard/python:latest-dev AS build
USER root
WORKDIR /app
COPY requirements.txt /app/
RUN python -m venv /opt/venv \
    && /opt/venv/bin/python -m pip install --no-cache-dir -r requirements.txt

FROM cgr.dev/chainguard/python:latest
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY *.py /app/
ENTRYPOINT ["/opt/venv/bin/python"]
CMD ["main.py"]
