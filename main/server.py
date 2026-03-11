import socket
import ssl
import json
import time
import os
import bcrypt

from jose import jwt,JWTError
from cryptography.fernet import Fernet

HOST="0.0.0.0"
PORT=8000

SECRET=os.getenv("OPENCHIRO_SECRET","devsecret")

PATIENT_FILE="patients.enc"
APPT_FILE="appointments.enc"
KEY_FILE="data.key"

# encryption key
if not os.path.exists(KEY_FILE):
    key=Fernet.generate_key()
    open(KEY_FILE,"wb").write(key)
else:
    key=open(KEY_FILE,"rb").read()

cipher=Fernet(key)

# users
users={
    "user":bcrypt.hashpw(b"pass1234",bcrypt.gensalt())
}


def load_file(path):

    if not os.path.exists(path):
        return []

    data=open(path,"rb").read()

    try:
        return json.loads(cipher.decrypt(data).decode())
    except:
        return []


def save_file(path,data):

    enc=cipher.encrypt(json.dumps(data).encode())
    open(path,"wb").write(enc)


def verify_token(token):

    try:
        payload=jwt.decode(token,SECRET,algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        return None


def handle(c):

    try:

        data=json.loads(c.recv(8192).decode())

        # LOGIN
        if "username" in data:

            u=data["username"]
            p=data["password"].encode()

            h=users.get(u)

            if not h or not bcrypt.checkpw(p,h):
                c.send(b'{"status":"fail"}')
                return

            token=jwt.encode(
                {"sub":u,"exp":int(time.time())+3600},
                SECRET,
                algorithm="HS256"
            )

            c.send(json.dumps({"token":token}).encode())
            return


        user=verify_token(data.get("token"))

        if not user:
            c.send(b'{"status":"unauthorized"}')
            return


        action=data.get("action")

        # CREATE PATIENT
        if action=="create_patient":

            patients=load_file(PATIENT_FILE)

            p=data["data"]
            p["id"]=len(patients)+1
            p["created_by"]=user

            p["soap"]=[]

            patients.append(p)

            save_file(PATIENT_FILE,patients)

            c.send(b'{"status":"ok"}')


        # LIST PATIENTS
        elif action=="list_patients":

            patients=load_file(PATIENT_FILE)

            c.send(json.dumps({
                "status":"ok",
                "patients":patients
            }).encode())


        # ADD SOAP NOTE
        elif action=="add_soap":

            patients=load_file(PATIENT_FILE)

            pid=data["patient_id"]
            note=data["soap"]

            for p in patients:

                if p["id"]==pid:

                    note["provider"]=user
                    note["time"]=int(time.time())

                    p["soap"].append(note)

            save_file(PATIENT_FILE,patients)

            c.send(b'{"status":"ok"}')


        # LIST SOAP NOTES
        elif action=="list_soap":

            patients=load_file(PATIENT_FILE)

            pid=data["patient_id"]

            for p in patients:

                if p["id"]==pid:

                    c.send(json.dumps({
                        "status":"ok",
                        "soap":p.get("soap",[])
                    }).encode())
                    return

            c.send(b'{"status":"not_found"}')


        # CREATE APPOINTMENT
        elif action=="create_appointment":

            appts=load_file(APPT_FILE)

            a=data["data"]

            a["id"]=len(appts)+1
            a["created_by"]=user

            appts.append(a)

            save_file(APPT_FILE,appts)

            c.send(b'{"status":"ok"}')


        # LIST APPOINTMENTS
        elif action=="list_appointments":

            appts=load_file(APPT_FILE)

            c.send(json.dumps({
                "status":"ok",
                "appointments":appts
            }).encode())


        else:
            c.send(b'{"status":"unknown"}')

    finally:
        c.close()


context=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain("cert.pem","key.pem")

with socket.socket() as s:

    s.bind((HOST,PORT))
    s.listen()

    with context.wrap_socket(s,server_side=True) as ss:

        print("OpenChiro Server Running on",PORT)

        while True:

            client,addr=ss.accept()

            handle(client)