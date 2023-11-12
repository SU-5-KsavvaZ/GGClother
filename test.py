import requests
import json

gen = 'мужчина'
weather = (2, 'Clouds')
preferences = ['кофты', 'джинсы']
headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOTYyZDkxZDktZTFiOC00YjVlLWJiNjktYzlmYzFiNmMzMmEwIiwidHlwZSI6ImFwaV90b2tlbiJ9.MnpC2h9x7Kl6-SMVUdrmA9xj8c326q4ZCP-A0V9qt3U"}
url = "https://api.edenai.run/v2/text/generation"
payload = {"providers": "openai,cohere",
               "text": f"generate clothes{gen} for situation, when on the street {weather[0]} degrees and {weather[1]} according to preferences: {preferences}, write it on russian language",
               "temperature": weather[0],
               "max_tokens": 250}
response = requests.post(url, json=payload, headers=headers)
result = json.loads(response.text)
print(result['openai']['generated_text'])