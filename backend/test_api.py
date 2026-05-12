import requests

url = "http://127.0.0.1:8000/ask"

payload = {
    "question": "How do I evolve Riolu?"
}

response = requests.post(url, json=payload)
print(response.json())
