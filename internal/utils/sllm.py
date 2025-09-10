import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLLM_API_URL = os.getenv("SLLM_API_URL")


url = SLLM_API_URL + "/api/v1/chat"
headers = {"Content-Type": "application/json"}


def run_sllm(history, permission="none", tone="formal"):
    data = {"history": history, "permission": permission, "tone": tone}

    response = requests.post(url, headers=headers, json=data)

    return response.json()["response"], response.json()["title"] 
