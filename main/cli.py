import socket
import ssl
import json
import getpass

from prompt_toolkit.shortcuts import (
    radiolist_dialog,
    message_dialog,
    input_dialog
)

HOST = "localhost"
PORT = 8000

print("#### OPENCHIRO ####")



u = input("login: ")
p = getpass.getpass("pass: ")

ctx = ssl._create_unverified_context()

def send_request(data):
    with ctx.wrap_socket(socket.socket(), server_hostname=HOST) as s:
        s.connect((HOST, PORT))
        s.send(json.dumps(data).encode())
        return json.loads(s.recv(8192).decode())

response = send_request({
    "username": u,
    "password": p
})

if "token" not in response:
    print("Login failed")
    exit()

token = response["token"]

message_dialog(
    title="Login Successful",
    text=f"Welcome {u}"
).run()




def create_patient():

    first = input_dialog(
        title="Create Patient",
        text="First Name:"
    ).run()

    if not first:
        return

    last = input_dialog(
        title="Create Patient",
        text="Last Name:"
    ).run()

    dob = input_dialog(
        title="Create Patient",
        text="DOB (YYYY-MM-DD):"
    ).run()

    phone = input_dialog(
        title="Create Patient",
        text="Phone:"
    ).run()

    email = input_dialog(
        title="Create Patient",
        text="Email:"
    ).run()

    patient = {
        "first_name": first,
        "last_name": last,
        "dob": dob,
        "phone": phone,
        "email": email
    }

    r = send_request({
        "token": token,
        "action": "create_patient",
        "data": patient
    })

    if r.get("status") == "ok":
        message_dialog(
            title="Patient Created",
            text=f"{first} {last} added successfully"
        ).run()
    else:
        message_dialog(
            title="Error",
            text="Failed to create patient"
        ).run()




def view_patients():

    r = send_request({
        "token": token,
        "action": "list_patients"
    })

    if r.get("status") != "ok":
        message_dialog(
            title="Error",
            text="Could not retrieve patients"
        ).run()
        return

    patients = r["patients"]

    if not patients:
        message_dialog(
            title="Patients",
            text="No patients found"
        ).run()
        return

    text = ""

    for p in patients:
        text += (
            f"ID: {p['id']}\n"
            f"Name: {p['first_name']} {p['last_name']}\n"
            f"DOB: {p['dob']}\n"
            f"Phone: {p['phone']}\n"
            f"Email: {p['email']}\n"
            f"Created By: {p['created_by']}\n"
            "-----------------------\n"
        )

    message_dialog(
        title="Patient List",
        text=text
    ).run()




def patient_menu():

    while True:

        choice = radiolist_dialog(
            title="Patients",
            text="Select an option",
            values=[
                ("create", "Create Patient"),
                ("view", "View Patients"),
                ("back", "Back")
            ]
        ).run()

        if choice == "create":
            create_patient()

        elif choice == "view":
            view_patients()

        elif choice == "back" or choice is None:
            break




def menu():

    while True:

        choice = radiolist_dialog(
            title="OpenChiro",
            text="Select an option",
            values=[
                ("patients", "Patient List"),
                ("schedule", "Schedule"),
                ("admin", "Admin"),
                ("logout", "Logout")
            ]
        ).run()

        if choice == "patients":
            patient_menu()

        elif choice == "schedule":
            message_dialog(
                title="Schedule",
                text="Schedule module coming soon"
            ).run()

        elif choice == "admin":
            message_dialog(
                title="Admin",
                text="Admin module coming soon"
            ).run()

        elif choice == "logout" or choice is None:
            print("Logged out")
            break


menu()
