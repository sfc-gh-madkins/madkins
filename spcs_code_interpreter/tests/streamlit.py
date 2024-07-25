### Environment Setup
import json
import time

import openai

import streamlit as st

from snowflake.snowpark import Session
from snowflake.ml.utils.connection_params import SnowflakeLoginOptions

client = openai.OpenAI()
session = Session.builder.configs(SnowflakeLoginOptions()).create()
SESSION_MODEL = "gpt-4-0125-preview"

################################################################################################################
### Assistant Setup

spcs_code_interpreter_execute_description = '''

This function allows you to execute python code in a stateful python execution environment, just like a jupyter notebook.
The following code has already been run:
```
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
session
```

Each time you call this function, the result of final line of code or bug message is returned.
For example, given the following question:
"What is x+y where x=1 and y=5"
The python program should look like this:
```
x=1
y=5
answer = x + y
answer
```
Notice how the variable "answer" is added again at the end to print out the answer.

To interact with the command line (bash), which you also have permission to do. Simply put a ! in front of the command.
For example, if you wanted to check whether you have access to a GPU first before you run code, you would run:
```
!nvidia-smi
```
This also will return the output coming from the terminal.
You cannot mix and match python and bash in a single call / cell.
'''
def spcs_code_interpreter_execute(code: str):
    sql = f'''SELECT MILES.SPCS_FUNCTIONS.SPCS_CODE_INTERPRETER_EXECUTE('{code.replace("'", '"')}') AS result;'''
    return session.sql(sql).collect()[0].as_dict()['RESULT']


spcs_code_interpreter_start_description = '''
This function gives you the ability to create a python execution environment when you want to write and test code.
Because the python environment this function creates is stateful, it can also be used to clear the environment and start fresh.
You need to call the function atleast once before you think about calling any of the other functions that relate to python.
'''
def spcs_code_interpreter_start():
    sql = f'''SELECT MILES.SPCS_FUNCTIONS.SPCS_CODE_INTERPRETER_RESTART();'''
    session.sql(sql).collect()
    return 'SUCCESFULLY STARTED/RESTARTED PYTHON ENVIRONMENT'


spcs_code_interpreter_environment_description = '''
This function allows you to retrieve all of the packages that are available in the python environment that you have spun up for writing and testing code.
You most likely only need to run this function once, right after you started the python environment.
In case you forget what packages are available though, feel free to run this as needed.
The main purpose of this function is to limit you to only writing code that will run properly with the given available packages.
'''
def spcs_code_interpreter_environment():
    sql = f'''SELECT MILES.SPCS_FUNCTIONS.SPCS_CODE_INTERPRETER_ENVIRONMENT() AS result;'''
    return session.sql(sql).collect()[0].as_dict()['RESULT']


_available_functions = {
    "spcs_code_interpreter_start": spcs_code_interpreter_start,
    "spcs_code_interpreter_execute": spcs_code_interpreter_execute,
    "spcs_code_interpreter_environment": spcs_code_interpreter_environment,
}

_function_tool_metadata = [
#    {"type": "code_interpreter"},
#    {"type": "retrieval"},
#    {"type": "function",
#        "function": {
#            "name": "spcs_code_interpreter_start",
#            "description": spcs_code_interpreter_start_description,
#            "parameters": {}
#        },
#            "required": []
#    },
    {"type": "function",
        "function": {
            "name": "spcs_code_interpreter_execute",
            "description": spcs_code_interpreter_execute_description,
            "parameters": {
                "type": "object",
                "properties": {
                    "code":  {
                        "type": "string",
                        "description": "Python code or bash/terminal commands to be executed"},
                    }
            },
            "required": ["code"]
        }
    },
#    {"type": "function",
#        "function": {
#            "name": "spcs_code_interpreter_environment",
#            "description": spcs_code_interpreter_environment_description,
#            "parameters": {}
#        },
#            "required": []
#    }
]

def _get_function_metadata(chosen: list) -> list:
    tools = [d for d in _function_tool_metadata if
             ('function' in d and d['function']['name'] in chosen) or d['type'] in chosen]
    return tools

name = 'spcs_code_interpreter'
instructions = '''
"You are a python developer with expert knowledge about data engineer and data science.
To do your job, you must always first create a python environment and grab the available packages, so you know what packages you have at your disposal to write code that will run.
Then, when asked a question, write and run code to answer the question."
Again, you cannot run "spcs_code_interpreter_execute" without first running "spcs_code_interpreter_start" and "spcs_code_interpreter_environment"
Please always use double quotes in your code where they are interchangeable with single quotes.
'''
tools = [
#    'retrieval',
#    'spcs_code_interpreter_start',
#    'spcs_code_interpreter_environment',
    'spcs_code_interpreter_execute'
]

assistants = [a for a in client.beta.assistants.list(order="desc", limit="20") if a.name == name]
assistant = client.beta.assistants.update(
    assistants[0].id,
    name=name,
    instructions=instructions,
    tools=_get_function_metadata(tools),
    model=SESSION_MODEL,
)

################################################################################################################
### Function Setup
def _execute_function_call(function_name, arguments):
    function = _available_functions.get(function_name, None)
    if function:
        arguments = json.loads(arguments)
        try:
            results = function(**arguments)
        except Exception as e:
            results = f"""Failed to execute the code because of error 
                <error>
                {str(e)}
                </error>
                Please fix the <error> and retry"""
    else:
        results = f"Error: function {function_name} does not exist"
    return results

def _get_function_details(run):
    function_details = []

    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        function_name = tool_call.function.name
        arguments = tool_call.function.arguments
        function_id = tool_call.id
        function_details.append((function_name, arguments, function_id))

    # print(function_details)
    return function_details

def _submit_tool_outputs(run, thread, responses):
    tool_outputs_list = []

    for response in responses:
        tool_outputs_list.append({
            "tool_call_id": response[0],
            "output": str(response[1])
        })

    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs_list
    )
    return run


################################################################################################################
#### Create Chat Thread

thread_id = client.beta.threads.create().id

query = '''
lets create another dataframe, df2, that takes the data from the word count column we created

'''

################################################################################################################
#### Converse

def execute_prompt(assistant_id, thread_id, prompt):

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id).status

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        time.sleep(1)
        if run.status == 'requires_action':
            function_details = _get_function_details(run)
            print(function_details)
            
            responses = []
            for function in function_details:
                function_response = _execute_function_call(function[0], function[1])
                responses.append((function[2], function_response))
                
            run = _submit_tool_outputs(run, thread, responses)
        elif run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            latest_message = messages.data[0]
            response = latest_message.content[0].text.value
            break

    return response



###

thread = client.beta.threads.retrieve(thread_id)

st.title("ChatGPT-like clone")


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = SESSION_MODEL

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = execute_prompt(assistant.id, thread.id, prompt)
        message_placeholder.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})