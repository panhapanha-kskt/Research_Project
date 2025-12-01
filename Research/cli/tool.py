import requests
import json

API_URL = "http://localhost:8000"
API_KEY = "supersecret123"  # must match backend/.env


def add_user():
    print("\nEnter User Information")
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    age = int(input("Age: "))

    payload = {
        "name": name,
        "email": email,
        "age": age
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    r = requests.post(f"{API_URL}/user", json=payload, headers=headers)

    if r.status_code == 200:
        data = r.json()
        print(data["message"])  # ✅ consistent spaces
    else:
        print("Error saving user:", r.text)


def view_users():
    headers = {"x-api-key": API_KEY}
    r = requests.get(f"{API_URL}/users", headers=headers)

    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        print("Error:", r.text)


def main():
    while True:
        print("\n=== User Information CLI ===")
        print("1. Add User")
        print("2. View Users")
        print("3. Exit")
        option = input("Choose an option: ")

        if option == "1":
            add_user()
        elif option == "2":
            view_users()
        elif option == "3":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
