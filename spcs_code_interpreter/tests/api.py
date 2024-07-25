import requests


def spcs_code_interpreter(gpt_payload):

    url = "http://localhost:8000/execute"
    headers = {"Content-Type": "application/json"}
    code = gpt_payload['python']

    data = {"code": code}
    response = requests.post(url, headers=headers, json=data)

    return response

def get_python_environment():
    url = "http://localhost:8000/environment"
    response = requests.get(url)
    return response

if __name__ == "__main__":
    gpt_payload = {'python': 'session.sql("select * from MILES.REINVENT.WIKI limit 10").to_pandas()'}
    result = get_python_environment()
    print(result.json())
    result = spcs_code_interpreter(gpt_payload)
    print(result.json())