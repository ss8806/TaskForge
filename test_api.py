import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_registration():
    url = f"{BASE_URL}/auth/register"
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_registration()
