from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import base64
import cloudpickle as cp
from snowflake.snowpark import Session
import os

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/test")
async def read_root_test():
    return {"Hello": "Test"}

@app.post("/test2")
async def read_root_test_post():
    return {"Hello": "Test Post"}

@app.post("/sp")
async def sp(payload: dict):
    session = Session.builder.configs(payload['connection_parameters']).create()

    func = cp.loads(base64.b64decode(payload['function'].encode()))
    result = func(session)
    print(result)
    return {'result': result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
