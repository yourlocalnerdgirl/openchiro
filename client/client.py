from prompt_toolkit.shortcuts import radiolist_dialog, message_dialog, input_dialog
from prompt_toolkit.formatted_text import HTML
import socket
import json
import ssl


HOST = "127.0.0.1"
PORT = 5678

CASE_COLORS = {
    "cash": "ansigreen",
    "insurance": "ansiblue",
    "personal injury": "ansired",
    "workers comp": "ansiyellow"
}




def schedule_board():
    res = send_request({
        "action": "list_all_appointments"
    })

    if not res:
        message_dialog(
            title="Schedule",
            text="No appointments scheduled."
        ).run()
        menu()
        return
    lines = []

    for appt in res:
        patient = appt["patient"]
        date = appt["date"]
        time = appt["time"]
        ctype = appt["ctype"]
        color = CASE_COLORS.get(ctype.lower(), "ansiwhite")
        lines.append(
            f"<{color}>{time}  {patient}  ({ctype})</{color}>"
        )
    schedule_text = "<br/>".join(lines)
    message_dialog(
        title="Appointment Schedule",
        text=HTML(schedule_text)
    ).run()

    menu()





def appointment_menu(pid):

    choice = radiolist_dialog(
        title="Appointments",
        values=[
            ("create", "Create Appointment"),
            ("view", "View Appointments"),
            ("delete", "Delete Appointment"),
            ("back", "Back")
        ]
    ).run()

    if choice == "create":

        date = input_dialog(
            title="Appointment",
            text="Date (YYYY-MM-DD):"
        ).run()

        time = input_dialog(
            title="Appointment",
            text="Time (HH:MM):"
        ).run()

        reason = input_dialog(
            title="Appointment",
            text="Reason:"
        ).run()

        send_request({
            "action": "create_appointment",
            "patient_id": pid,
            "date": date,
            "time": time,
            "reason": reason
        })

        message_dialog(
            title="Appointment",
            text="Appointment created."
        ).run()

        appointment_menu(pid)





def soap_menu(pid):

    vertebrae = [
        "C1","C2","C3","C4","C5","C6","C7",
        "T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12",
        "L1","L2","L3","L4","L5",
        "S1"
    ]

    choices = []

    for v in vertebrae:
        choices.append((v, v))

    choices.append(("back", "Back"))

    selected = radiolist_dialog(
        title="SOAP Notes - Select Vertebra",
        values=choices
    ).run()

    if selected == "back" or selected is None:
        patient_menu(pid)
        return


    # get existing note
    res = send_request({
        "action": "get_soap",
        "id": pid,
        "vertebra": selected
    })

    note = res["note"]


    newnote = input_dialog(
        title=f"SOAP Note ({selected})",
        text=f"Existing note:\n\n{note}\n\nEnter new / updated note:"
    ).run()

    if newnote is None:
        soap_menu(pid)
        return


    send_request({
        "action": "save_soap",
        "id": pid,
        "vertebra": selected,
        "note": newnote
    })

    message_dialog(
        title="SOAP Saved",
        text=f"SOAP note saved for {selected}"
    ).run()

    soap_menu(pid)







def send_request(data):
    ctx = ssl._create_unverified_context()
    with ctx.wrap_socket(socket.socket(), server_hostname=HOST) as s:
        s.connect((HOST, PORT))
        s.send(json.dumps(data).encode())
        res = s.recv(4096)
        return json.loads(res.decode())




def createpatient():
    fname = input_dialog(
        title="Create Patient",
        text="First Name:"
    ).run()
    lname = input_dialog(
        title="Create Patient",
        text="Last Name:"
    ).run()
    dob = input_dialog(
        title="Create Patient",
        text="DOB:"
    ).run()
    ssn = input_dialog(
        title="Create Patient",
        text="SSN:"
    ).run()
    case = input_dialog(
        title="Create Patient",
        text="Case Type:"
    ).run()

    data = {
        "action": "create_patient",
        "firstname": fname,
        "lastname": lname,
        "dob": dob,
        "ssn": ssn,
        "ctype": case
    }

    res = send_request(data)
    patientlist()

def deletepatient():
    return







def patient_menu(pid):

    choice = radiolist_dialog(
        title="Patient Menu",
        text="Select an option:",
        values=[
            ("demo", "Demographics"),
            ("soap", "SOAP Notes (Spine)"),
            ("billing", "Billing (Not implemented)"),
            ("app", "Appointments"),
            ("back", "Back")
        ]
    ).run()

    if choice == "demo":

        demo = send_request({
            "action": "get_demographics",
            "id": pid
        })

        info = f"""
    ID: {demo["id"]}
    Name: {demo["firstname"]} {demo["lastname"]}
    DOB: {demo["dob"]}
    SSN: {demo["ssn"]}
    Case Type: {demo["ctype"]}
    """

        message_dialog(
            title="Patient Demographics",
            text=info
        ).run()

        patient_menu(pid)

    elif choice == "soap":
        soap_menu(pid)

        patient_menu(pid)

    elif choice == "billing":

        message_dialog(
            title="Billing",
            text="Billing system not implemented yet."
        ).run()

        patient_menu(pid)
    elif choice== "app":
        appointment_menu(pid)
        
        
    elif choice == "back":
        viewpatients()








def viewpatients():

    response = send_request({
        "action": "list_patients"
    })

    patients = response

    if not patients:
        message_dialog(
            title="Patients",
            text="No patients found."
        ).run()
        patientlist()
        return

    choices = []

    for p in patients:
        choices.append((p["id"], f'{p["id"]} - {p["name"]}'))

    choices.append(("back", "Back"))

    selected = radiolist_dialog(
        title="Patient List",
        text="Select a patient:",
        values=choices
    ).run()

    if selected == "back" or selected is None:
        patientlist()
        return

    patient_menu(selected)





def patientlist():
    pchoice = radiolist_dialog(
        title="Patients",
        values=[
            ("createp", "Create Patient"),
            ("deletep", "Delete Patient"),
            ("viewp", "View Patients"),
            ("back", "Back")
        ]
    ).run()

    if pchoice =="createp":
        createpatient()
    elif pchoice =="deletep":
        deletepatient()
    elif pchoice=="viewp":
        viewpatients()
    elif pchoice=="back":
        menu()



def menu():
    choice = radiolist_dialog(
        title="OpenChiro Main Menu",
        values=[
            ("patients", "Patient List and Selection"),
            ("app", "Appointments"),
            ("exit", "Log Out")
        ]
    ).run()

    if choice =="patients":
        patientlist()
    elif choice=="app":
        schedule_board()
    elif choice =="exit":
        exit()


login = input_dialog(
    title="OpenChiro Login",
    text="Username:"

).run()

password = input_dialog(
    title="OpenChiro Login",
    text="Password:"
).run()


data = {
    "username": login,
    "password": password
}

ctx = ssl._create_unverified_context()

with ctx.wrap_socket(socket.socket(), server_hostname=HOST) as s:
    s.connect((HOST, PORT))
    s.send(json.dumps(data).encode())
    sres = s.recv(1024)
    if sres == b'ok':
        menu()




menu()