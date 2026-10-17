import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "ministral-3:8b",
    "prompt": "Explica en una frase qué es un modelo de lenguaje.",
    "stream": False
}

response = requests.post(url, json=payload, timeout=120)
response.raise_for_status()

data = response.json()

print("Respuesta del modelo:")
print(data["response"])