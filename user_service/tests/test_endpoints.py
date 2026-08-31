import os, sys


sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from run import app

# Create a local testing context
client = app.test_client()

def test_user_creation():
    payload = {"first_name": "naval", "last_name": "shankhdhar", "email": "navalshankhdharlife@gmail.com", "password": "naval@123456"}
    
    # Simulate a real HTTP POST request
    response = client.post('/api/users/registration', json=payload)
    
    print("\n--- TEST RESPONSE ---")
    print(f"Status Code: {response.status_code}")
    print(f"Data: {response.get_json()}")


def test_login():
    payload = {"email": "navalshankhdharlife@gmail.com", "password": "naval@123456"}
    
    # Simulate a real HTTP POST request
    response = client.post('/api/users/login', json=payload)
    
    print("\n--- TEST RESPONSE ---")
    print(f"Status Code: {response.status_code}")
    print(f"Data: {response.get_json()}")

def test_product_list():
    # Simulate a real HTTP GET request
    headers = {
        "Authorization": "Bearer xyz"
    }
    response = client.get('/api/users/list?page=1&per_page=20', headers=headers)
    
    print("\n--- TEST RESPONSE ---")
    print(f"Status Code: {response.status_code}")
    print(f"Data: {response.get_json()}")

