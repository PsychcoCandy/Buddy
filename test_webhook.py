import requests

url = "http://127.0.0.1:5000/webhook"

data = {
    "entry": [
        {
            "changes": [
                {
                    "value": {
                        "messages": [
                            {
                                "from": "919876543210",
                                "id": "message_123",
                                "type": "text",
                                "text": {
                                    "body": "I want 2 kg chicken"
                                }
                            }
                        ]
                    }
                }
            ]
        }
    ]
}

response = requests.post(url, json=data)

print("Status:", response.status_code)
print("Response:", response.text)