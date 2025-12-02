import requests
import json
import getpass
import os
from datetime import datetime

API_URL = "http://localhost:8000"
API_KEY = "supersecret123"
SESSION_FILE = "session.json"


def load_session():
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE, "r") as f:
        return json.load(f)


def save_session(session: dict):
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f)


class CloudflareCloneCLI:
    def __init__(self):
        self.session = load_session()
        self.token = self.session.get("token")
        self.headers = {"x-api-key": API_KEY}
        if self.token:
            self.headers["token"] = self.token  # Send token in header for Zero Trust

    # ===========================================================
    # LOGIN (ZERO TRUST)
    # ===========================================================
    def login(self):
        """Generate Zero Trust token"""
        response = requests.post(
            f"{API_URL}/auth/token",
            headers=self.headers
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print("✅ Successfully authenticated with Zero Trust")
            self.session["token"] = self.token
            save_session(self.session)
            self.headers["token"] = self.token  # Always include token for future requests
            return True
        else:
            print("❌ Authentication failed:", response.text)
            return False

    # ===========================================================
    # USER MANAGEMENT
    # ===========================================================
    def manage_users(self):
        while True:
            print("\n=== User Management ===")
            print("1. Add User")
            print("2. View Users")
            print("3. View Current User (Zero Trust)")
            print("4. Back to Main")

            choice = input("Choose: ")

            if choice == "1":
                self.add_user()
            elif choice == "2":
                self.view_users()
            elif choice == "3":
                self.get_current_user()
            elif choice == "4":
                break

    def add_user(self):
        print("\n=== Add User ===")
        name = input("Name: ")
        email = input("Email: ")
        age = input("Age: ")

        try:
            payload = {"name": name, "email": email, "age": int(age)}
        except ValueError:
            print("❌ Age must be a number")
            return

        response = requests.post(
            f"{API_URL}/user",
            headers=self.headers,
            json=payload
        )

        if response.status_code == 200:
            print("✅ User added successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print("❌ Error:", response.text)

    def view_users(self):
        print("\n=== Registered Users ===")
        response = requests.get(f"{API_URL}/users", headers=self.headers)
        if response.status_code == 200:
            users = response.json()
            if not users:
                print("No users found.")
                return
            for u in users:
                print(f"- ID: {u['id']}, Name: {u['name']}, Email: {u['email']}, Age: {u['age']}")
        else:
            print("❌ Error:", response.text)

    def get_current_user(self):
        if not self.token:
            print("⚠ Please login first (option 5)")
            return

        response = requests.get(f"{API_URL}/users/me", headers=self.headers)
        if response.status_code == 200:
            print("\n" + json.dumps(response.json(), indent=2))
        else:
            print("❌ Error:", response.text)

    # ===========================================================
    # ANALYTICS (DASHBOARD)
    # ===========================================================
    def analytics_dashboard(self):
        response = requests.get(f"{API_URL}/analytics/overview", headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            print("\n📊 API Analytics Dashboard")
            print("=" * 40)
            print(f"📅 Date: {data.get('date')}")
            print(f"📨 Total Requests: {data.get('total_requests')}")
            print(f"⚡ Avg Response Time: {data.get('avg_response_time_ms')}ms")
            print(f"👥 Total Users: {data.get('total_users', 'N/A')}")
            print(f"🔑 Total Secrets: {data.get('total_secrets', 'N/A')}")

            top_eps = data.get('top_endpoints', [])
            if top_eps:
                print("\n🏆 Top Endpoints:")
                for endpoint in top_eps:
                    print(f"  {endpoint['endpoint']}: {endpoint['count']} requests")
            else:
                print("\n🏆 Top Endpoints: No activity yet.")

            view_logs = input("\nView detailed logs? (y/n): ")
            if view_logs.lower() == 'y':
                self.view_audit_logs()
        else:
            print("❌ Error:", response.text)
    def view_audit_logs(self, limit: int = 20):
        response = requests.get(f"{API_URL}/analytics/logs?limit={limit}", headers=self.headers)
        if response.status_code == 200:
            logs = response.json()
            print(f"\n🔍 Last {len(logs)} Audit Logs")
            print("=" * 60)
            for log in logs:
                ts = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                print(f"{ts} | {log['method']} {log['endpoint']} | "
                      f"{log['status_code']} | {log['client_id']} | "
                      f"{log['response_time_ms']}ms")
        else:
            print("❌ Error:", response.text)

    # ===========================================================
    # SECRETS MANAGEMENT
    # ===========================================================
    def secrets_management(self):
        while True:
            print("\n=== Secrets Management ===")
            print("1. Create Secret")
            print("2. Get Secret")
            print("3. Rotate Secret")
            print("4. Back to Main")

            choice = input("Choose: ")

            if choice == "1":
                name = input("Secret name: ")
                value = getpass.getpass("Secret value: ")
                description = input("Description (optional): ")
                response = requests.post(
                    f"{API_URL}/secrets?name={name}&value={value}&description={description}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    print("✅ Secret created")
                else:
                    print("❌ Error:", response.text)

            elif choice == "2":
                name = input("Secret name: ")
                response = requests.get(f"{API_URL}/secrets/{name}", headers=self.headers)
                if response.status_code == 200:
                    sec = response.json()
                    print(f"\n🔐 Secret: {sec['name']}")
                    print(f"Value: {sec['value']}")
                    if sec.get('description'):
                        print(f"Description: {sec['description']}")
                else:
                    print("❌ Error:", response.text)

            elif choice == "3":
                name = input("Secret name: ")
                new_value = getpass.getpass("New secret value: ")
                response = requests.post(
                    f"{API_URL}/secrets/{name}/rotate?new_value={new_value}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    print("✅ Secret rotated")
                else:
                    print("❌ Error:", response.text)

            elif choice == "4":
                break

    # ===========================================================
    # MAIN MENU
    # ===========================================================
    def run(self):
        while True:
            print("\n=== Cloudflare Clone CLI ===")
            print("1. User Management")
            print("2. API Analytics Dashboard")
            print("3. Secrets Management")
            print("4. View Audit Logs")
            print("5. Login (Zero Trust)")
            print("6. Exit")

            choice = input("Choose: ")

            if choice == "1":
                self.manage_users()
            elif choice == "2":
                self.analytics_dashboard()
            elif choice == "3":
                self.secrets_management()
            elif choice == "4":
                self.view_audit_logs()
            elif choice == "5":
                self.login()
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice")


# ===========================================================
# START CLI
# ===========================================================
if __name__ == "__main__":
    cli = CloudflareCloneCLI()
    cli.run()
