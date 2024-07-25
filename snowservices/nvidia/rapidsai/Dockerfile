FROM rapidsai/rapidsai:23.04-cuda11.8-runtime-ubuntu22.04-py3.8

WORKDIR /snowflake_nvidia

ADD server.py ./server.py

RUN pip install fastapi uvicorn cloudpickle snowflake-snowpark-python[pandas]

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
