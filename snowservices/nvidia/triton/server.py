from fastapi import FastAPI
import uvicorn

import pandas as pd

import tritonclient.grpc as triton_grpc
from tritonclient import utils as triton_utils

app = FastAPI()

@app.post("/")
async def sp(payload: dict):

    df = pd.DataFrame(payload['data'])
    #df[0] = index 1-n...
    #df[1] = input #1
    #df[2] = input #2 ...

    #{'data': [[0, 1001, 's'], [1, 1002, 's'], [2, 1003, 's'], [3, 1004, 's'], [4, 1005, 's']]}
    #{'data': [[index, col1 row1, col2 row1], [index, col2 row2, col2 row2]]}








    #result_content = {'data': result_list_of_list}
    #{'data': [[index, inference1], [index, inference]]}
    return {'data': df[[0,1]].values.tolist()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
