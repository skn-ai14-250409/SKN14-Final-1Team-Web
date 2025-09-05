import requests

url = "http://sllm.code-nova.dev:8001/api/v1/chat"
headers = {
    "Content-Type": "application/json"
}

def run_sllm(question):
    data = {
        "history": [
            {"type": "user", "content": question},
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    return response.json()['response']