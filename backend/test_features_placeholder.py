import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def login(username, password):
    response = requests.post(f"{BASE_URL}/auth/login/access-token", data={
        "username": username,
        "password": password
    })
    if response.status_code != 200:
        print(f"Login failed for {username}: {response.text}")
        return None
    return response.json()["access_token"]

def cleanup_user(username, token):
    # Find user
    headers = {"Authorization": f"Bearer {token}"}
    users = requests.get(f"{BASE_URL}/users/", headers=headers).json()
    for u in users:
        if u["username"] == username:
            requests.delete(f"{BASE_URL}/users/{u['id']}", headers=headers)
            print(f"Cleaned up user {username}")

def run_tests():
    print("--- Starting Backend Feature Tests ---")

    # 1. Login as Admin (assuming 'admin' exists from init_db or previous setup)
    # Based on previous context, there is likely an admin account. 
    # Usually admin/admin or similar. Let's try to find credentials or create a fresh one if possible?
    # Since I don't have the password, I might need to rely on the fact that I can see the DB or know default creds.
    # checking init_db might reveal default creds.
    
    # For now, let's assume we can use the test_users.txt if it exists, or defaults.
    # Let's try 'admin@example.com' / 'admin' which is common, or I'll check init_db first.
    pass

if __name__ == "__main__":
    pass
