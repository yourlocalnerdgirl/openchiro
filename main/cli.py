import socket, ssl, json, getpass
from prompt_toolkit.shortcuts import radiolist_dialog, message_dialog

HOST="localhost"
PORT=8000

print("#### OPENCHIRO ####")

u = input("login: ")
p = getpass.getpass("pass: ")

ctx = ssl._create_unverified_context()

with ctx.wrap_socket(socket.socket(), server_hostname=HOST) as s:
    s.connect((HOST,PORT))
    s.send(json.dumps({"username":u,"password":p}).encode())
    response = json.loads(s.recv(2048).decode())

if "token" not in response:
    print("Login failed")
    exit()

token = response["token"]

message_dialog(
    title="Login Successful",
    text=f"Welcome {u}"
).run()


def menu():
    while True:

        choice = radiolist_dialog(
            title="OpenChiro",
            text="Select an option",
            values=[
                ("patients","Patient List"),
                ("schedule","Schedule"),
                ("settings","Admin"),
                ("logout","Logout")
            ]
        ).run()

        if choice == "patients":
            message_dialog(
                title="Patients",
                text="Patient module coming soon"
            ).run()

        elif choice == "schedule":
            message_dialog(
                title="Schedule",
                text="Schedule module coming soon"
            ).run()

        elif choice == "Admin":
            message_dialog(
                title="Settings",
                text="Admin module coming soon"
            ).run()

        elif choice == "logout":
            print("Logged out")
            break


menu()