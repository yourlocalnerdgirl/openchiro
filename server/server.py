import socket
import ssl
import json
import os



if os.path.exists("appointments.json"):
    with open("appointments.json", "r") as f:
        appointments = json.load(f)
else:
    appointments = []


if os.path.exists("patients.json"):
    with open("patients.json", "r") as f:
        patients = json.load(f)
else:
    patients = []

next_id = 1

#bind port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5678))
server.listen()
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("cert.pem", "key.pem")
print("server up")

def save_appointments():
    with open("appointments.json", "w") as f:
        json.dump(appointments, f, indent=4)


def save_patients():
    with open("patients.json", "w") as f:
        json.dump(patients, f, indent=4)


while True:

    client, addr = server.accept()
    print("Connection from", addr)

    client = context.wrap_socket(client, server_side=True)

    data = client.recv(4096)

    if not data:
        client.close()
        continue
    decoded = json.loads(data.decode())

    print(decoded)
    #login
    if "username" in decoded:

        if decoded["username"] == "sky" and decoded["password"] == "pass1234":
            client.send(b"ok")
            print("login ok")
        else:
            client.send(b"fail")
            print("login fail!")

    #actions
    elif "action" in decoded:
        action = decoded["action"]
        #create
        if action == "create_patient":

            patient = {
                "id": max([p["id"] for p in patients], default=0) + 1,
                "firstname": decoded["firstname"],
                "lastname": decoded["lastname"],
                "dob": decoded["dob"],
                "ssn": decoded["ssn"],
                "ctype": decoded["ctype"],
                "soap": {}
            }

            patients.append(patient)
            save_patients()
            client.send(json.dumps({"status":"created"}).encode())


        #list
        elif action == "list_patients":
            plist = []
            for p in patients:
                plist.append({
                    "id": p["id"],
                    "name": p["firstname"] + " " + p["lastname"]
                })

            client.send(json.dumps(plist).encode())


        #get demos
        elif action == "get_demographics":
            pid = decoded["id"]
            for p in patients:
                if p["id"] == pid:
                    client.send(json.dumps(p).encode())
                    break


        #delete patient
        elif action == "delete_patient":
            pid = decoded["id"]
            patients[:] = [p for p in patients if p["id"] != pid]
            save_patients()
            client.send(json.dumps({"status":"deleted"}).encode())


        #save SOAP note
        elif action == "save_soap":
            pid = decoded["id"]
            vertebra = decoded["vertebra"]
            note = decoded["note"]
            for p in patients:
                if p["id"] == pid:
                    if "soap" not in p:
                        p["soap"] = {}
                    p["soap"][vertebra] = note
                    save_patients()
                    client.send(json.dumps({"status":"saved"}).encode())
                    break

        #get SOAP note
        elif action == "get_soap":
            pid = decoded["id"]
            vertebra = decoded["vertebra"]
            for p in patients:
                if p["id"] == pid:
                    note = ""
                    if "soap" in p and vertebra in p["soap"]:
                        note = p["soap"][vertebra]
                    client.send(json.dumps({"note": note}).encode())
                    break
                
        elif action == "create_appointment":

            appt = {
            "id": max([a["id"] for a in appointments], default=0) + 1,
            "patient_id": decoded["patient_id"],
            "date": decoded["date"],
            "time": decoded["time"],
            "reason": decoded["reason"]
        }

            appointments.append(appt)
            save_appointments()

            client.send(json.dumps({"status":"created"}).encode())

        elif action == "list_appointments":
        
            pid = decoded["patient_id"]

            plist = []
            for a in appointments:
                if a["patient_id"] == pid:
                    plist.append(a)

            client.send(json.dumps(plist).encode())

        elif action == "delete_appointment":

            aid = decoded["id"]

            appointments[:] = [a for a in appointments if a["id"] != aid]

            save_appointments()

            client.send(json.dumps({"status":"deleted"}).encode())


        elif action == "list_all_appointments":
            output = []
            for a in appointments:
                pid = a["patient_id"]
                for p in patients:
                    if p["id"] == pid:
                        output.append({
                        "id": a["id"],
                        "patient": p["firstname"] + " " + p["lastname"],
                        "date": a["date"],
                        "time": a["time"],
                        "ctype": p["ctype"]
                        })

            client.send(json.dumps(output).encode())

    client.close()