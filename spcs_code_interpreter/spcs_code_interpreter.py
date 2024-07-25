import os

from fastapi import FastAPI
from pydantic import BaseModel

from jupyter_client import KernelManager
import pkg_resources


class PythonExecutionEnvironment:
    def __init__(self):
        self.kernel_manager = KernelManager()
        self.kernel_manager.start_kernel()
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()

    def execute_code(self, code: str):
        self.kernel_client.execute(code)
        output = ''
        # Loop to capture all messages related to the execution
        while True:
            msg = self.kernel_client.get_iopub_msg()

            msg_type = msg['msg_type']
            if msg_type == 'execute_result':
                output = msg['content']['data']['text/plain']
            elif msg_type == 'stream':
                output = msg['content']['text']
            elif msg_type == 'error':
                output = msg['content']['traceback']
            elif msg_type == 'status' and msg['content']['execution_state'] == 'idle':
                break

        return output
    
python_kernel = PythonExecutionEnvironment()


def start_python_session(python_kernel: PythonExecutionEnvironment):
    if os.path.exists('/snowflake/session/token'):

        code = '''
import os
from snowflake.snowpark import Session

def get_login_token():
    with open('/snowflake/session/token', 'r') as f:
        return f.read()

connection_parameters = {
    "host": os.getenv('SNOWFLAKE_HOST'),
    "account": os.getenv('SNOWFLAKE_ACCOUNT'),
    "token": get_login_token(),
    "authenticator": "oauth",
}
session = Session.builder.configs(connection_parameters).create() 
        '''

    else:

        code = '''
from snowflake.snowpark import Session
from snowflake.ml.utils.connection_params import SnowflakeLoginOptions
 
session = Session.builder.configs(SnowflakeLoginOptions()).create()
        '''

    python_kernel.execute_code(code)
    return "Python session started"


def lifespan(app: FastAPI):
    start_python_session(python_kernel)
    yield
    python_kernel.kernel_manager.shutdown_kernel()

app = FastAPI(lifespan=lifespan)

@app.post("/identity")
async def post_identity(payload: dict):
    return payload


@app.post("/environment")
def get_available_packages():
    installed_packages = ', '.join(sorted(["%s==%s" % (i.key, i.version) for i in pkg_resources.working_set]))
    return {'data': [[0, installed_packages]]}


@app.post("/execute")
def execute_code(payload: dict):
    code = payload['data'][0][1]
    result = python_kernel.execute_code(code)
    return {'data': [[0, result]]}


@app.post("/restart")
def restart_kernel():
    python_kernel.kernel_manager.restart_kernel(now=True)
    start_python_session(python_kernel)
    return {'data': [[0, 'Kernel restarted']]}