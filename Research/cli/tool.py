import requests
import sys

API_URL = "http://localhost:8000"


def menu():
    print("\n=== User Information CLI ===")
    print("1. Add User")
    print("2. View Users")
    print("3. Exit")
    return input("Choose an option: ")


def add_user():
    print("\nEnter User Information")
    name = input("Name: ")
    email = input("Email: ")
    age = input("Age: ")

    try:
        age = int(age)
    except ValueError:
        print("Invalid age.")
        return

    data = {
        "name": name,
        "email": email,
        "age": age
    }

    res = requests.post(f"{API_URL}/user", params=data)

    if res.status_code == 200:
        print("User saved successfully!")
    else:
        print("Error saving user:", res.text)


def view_users():
    res = requests.get(f"{API_URL}/users")
    if res.status_code == 200:
        users = res.json()
        print("\n=== Users ===")
        for u in users:
            print(f"ID: {u['id']} | {u['name']} | {u['email']} | Age: {u['age']}")
    else:
        print("Error fetching users")


def main():
    while True:
        choice = menu()
        if choice == "1":
            add_user()
        elif choice == "2":
            view_users()
        elif choice == "3":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
