import socket
import ssl
import json
import time
import os
import bcrypt
from jose import jwt, JWTError
from cryptography.fernet import Fernet

HOST="0.0.0.0"
PORT=8000

SECRET=os.getenv("SKY2011","MAIN1")

DATA_FILE="patients.enc"
APPT_FILE="appointments.enc"
KEY_FILE="data.key"



if not os.path.exists(KEY_FILE):
    key=Fernet.generate_key()
    with open(KEY_FILE,"wb") as f:
        f.write(key)
else:
    with open(KEY_FILE,"rb") as f:
        key=f.read()

cipher=Fernet(key)



users={
    "molly":bcrypt.hashpw(b"pass1234",bcrypt.gensalt())
}



def load_file(path):
    if not os.path.exists(path):
        return []

    with open(path,"rb") as f:
        data=f.read()

    return json.loads(cipher.decrypt(data).decode())

def save_file(path,data):
    enc=cipher.encrypt(json.dumps(data).encode())

    with open(path,"wb") as f:
        f.write(enc)



def verify_token(token):
    try:
        payload=jwt.decode(token,SECRET,algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        return None



def handle(c):

    try:

        data=json.loads(c.recv(4096).decode())


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


        token=data.get("token")
        user=verify_token(token)

        if not user:
            c.send(b'{"status":"unauthorized"}')
            return

        action=data.get("action")

        if action=="create_patient":

            patients=load_file(DATA_FILE)

            p=data["data"]
            p["id"]=len(patients)+1
            p["created_by"]=user
            p["created_at"]=int(time.time())

            patients.append(p)

            save_file(DATA_FILE,patients)

            c.send(json.dumps({"status":"ok","patient":p}).encode())


        elif action=="list_patients":

            patients=load_file(DATA_FILE)

            c.send(json.dumps({
                "status":"ok",
                "patients":patients
            }).encode())

        elif action=="create_appointment":

            appts=load_file(APPT_FILE)

            a=data["data"]
            a["id"]=len(appts)+1

            appts.append(a)

            save_file(APPT_FILE,appts)

            c.send(json.dumps({"status":"ok"}).encode())


        elif action=="list_appointments":

            appts=load_file(APPT_FILE)

            pid=data.get("patient_id")

            if pid:
                appts=[a for a in appts if a["patient_id"]==pid]

            c.send(json.dumps({
                "status":"ok",
                "appointments":appts
            }).encode())

        else:
            c.send(b'{"status":"unknown_action"}')

    finally:
        c.close()



context=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain("cert.pem","key.pem")

with socket.socket() as s:

    s.bind((HOST,PORT))
    s.listen()

    with context.wrap_socket(s,server_side=True) as ss:

        print("OpenChiro Server Running on",PORT)
        print("Made by Sky Keefe for BTHFC")

        while True:
            client,_=ss.accept()
            handle(client)