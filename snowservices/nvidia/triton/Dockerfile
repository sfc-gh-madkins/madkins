FROM python:3.8-slim

WORKDIR /snowflake_nvidia

ADD server.py ./server.py

RUN pip install fastapi uvicorn snowflake-snowpark-python[pandas] tritonclient[all]

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
