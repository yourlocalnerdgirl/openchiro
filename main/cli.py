import socket
import ssl
import json
import getpass

from prompt_toolkit.shortcuts import radiolist_dialog,message_dialog,input_dialog

HOST="localhost"
PORT=8000

print("####OPENCHIRO####")

u=input("login: ")
p=getpass.getpass("pass: ")

ctx=ssl._create_unverified_context()

def send_request(data):
    with ctx.wrap_socket(socket.socket(),server_hostname=HOST) as s:
        s.connect((HOST,PORT))
        s.send(json.dumps(data).encode())
        return json.loads(s.recv(8192).decode())

response=send_request({"username":u,"password":p})

if "token" not in response:
    print("SERVER RESPONSE INVALID")
    exit()

token=response["token"]

message_dialog(
    title="Login Successful",
    text=f"Welcome, {u}!"
).run()


def create_patient():

    first=input_dialog(title="Create Patient",text="First Name:").run()
    if not first:
        return

    last=input_dialog(title="Create Patient",text="Last Name:").run()
    dob=input_dialog(title="Create Patient",text="DOB:").run()
    ssn=input_dialog(title="Create Patient",text="SSN:").run()
    phone=input_dialog(title="Create Patient",text="Phone:").run()
    email=input_dialog(title="Create Patient",text="Email:").run()
    ctype=input_dialog(title="Create Patient",text="Case Type? (Cash, Credit, Debit?)").run()

    patient={
        "first_name":first,
        "last_name":last,
        "dob":dob,
        "ssn":ssn,
        "phone":phone,
        "email":email,
        "ctype1":ctype
    }

    r=send_request({
        "token":token,
        "action":"create_patient",
        "data":patient
    })

    if r.get("status")=="ok":
        message_dialog(title="Success",text="Patient created").run()

def patient_chart(p):

    while True:

        choice=radiolist_dialog(
            title=f"{p['first_name']} {p['last_name']}",
            text="Patient Chart",
            values=[
                ("demo","Demographics"),
                ("appts","Appointments"),
                ("back","Back")
            ]
        ).run()

        if choice=="demo":

            text=f"""
            Name: {p['first_name']} {p['last_name']}
            DOB: {p['dob']}
            SSN: {p['ssn']}
            Phone: {p['phone']}
            Email: {p['email']}
            Case Type: {p.get('ctype1','Unknown')}
            """

            message_dialog(title="Demographics",text=text).run()

        elif choice=="appts":
            patient_appointments(p)

        else:
            break



def patient_appointments(p):

    r=send_request({
        "token":token,
        "action":"list_appointments",
        "patient_id":p["id"]
    })

    appts=r["appointments"]

    text=""

    for a in appts:
        text+=f"{a['date']} {a['time']} {a['provider']}\n"

    if not text:
        text="No appointments"

    message_dialog(title="Appointments",text=text).run()

def view_patients():

    r=send_request({
        "token":token,
        "action":"list_patients"
    })

    
    patients=r["patients"]

    if not patients:
        message_dialog(
            title="Patients",
            text="No patients found. Create one first."
        ).run()
        return
    
    values=[]

    for p in patients:
        label=f"{p['id']} {p['first_name']} {p['last_name']}"
        values.append((p,label))

    sel=radiolist_dialog(
        title="Patients",
        text="Select patient",
        values=values
    ).run()

    if sel:
        patient_chart(sel)

def create_appointment():

    pid=input_dialog(title="Create Appointment",text="Patient ID:").run()
    name=input_dialog(title="Create Appointment",text="Name:").run()
    date=input_dialog(title="Create Appointment",text="Date YYYY-MM-DD:").run()
    time=input_dialog(title="Create Appointment",text="Time HH:MM:").run()
    provider=input_dialog(title="Create Appointment",text="Provider:").run()
    room=input_dialog(title="Create Appointment",text="Room:").run()

    send_request({
        "token":token,
        "action":"create_appointment",
        "data":{
            "patient_id":int(pid),
            "date":date,
            "time":time,
            "provider":provider,
            "room":room,
            "name":name
        }
    })

    message_dialog(title="Appointment",text="Created").run()

def view_appointments():

    r=send_request({
        "token":token,
        "action":"list_appointments"
    })

    text=""

    for a in r["appointments"]:
        text+=f"Patient {a['name']} Has an Appointment on: {a['date']} at: {a['time']} with: {a['provider']} in: {a['room']} \n"

    if not text:
        text="No appointments"

    message_dialog(title="Appointments",text=text).run()

def scheduler():

    while True:

        choice=radiolist_dialog(
            title="Scheduler",
            text="Options",
            values=[
                ("create","Create Appointment"),
                ("view","View Appointments"),
                ("back","Back")
            ]
        ).run()

        if choice=="create":
            create_appointment()

        elif choice=="view":
            view_appointments()

        else:
            break

def patient_menu():

    while True:

        choice=radiolist_dialog(
            title="Patients",
            text="Options",
            values=[
                ("create","Create Patient"),
                ("view","View Patients"),
                ("back","Back")
            ]
        ).run()

        if choice=="create":
            create_patient()

        elif choice=="view":
            view_patients()

        else:
            break

def menu():

    while True:

        choice=radiolist_dialog(
            title="OpenChiro",
            text="Select option",
            values=[
                ("patients","Patient List"),
                ("schedule","Scheduler"),
                ("logout","Logout")
            ]
        ).run()

        if choice=="patients":
            patient_menu()

        elif choice=="schedule":
            scheduler()

        else:
            break

menu()