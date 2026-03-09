import socket
import ssl
import json
import time
import os
import bcrypt
from jose import jwt, JWTError
from cryptography.fernet import Fernet

HOST = "0.0.0.0"
PORT = 8000

SECRET = os.getenv("SKY2011", "MAIN1")

DATA_FILE = "patients.enc"
KEY_FILE = "data.key"


if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()

cipher = Fernet(key)


users = {
    "molly": bcrypt.hashpw(b"pass1234", bcrypt.gensalt())
}


def load_patients():

    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "rb") as f:
        encrypted = f.read()

    decrypted = cipher.decrypt(encrypted)

    return json.loads(decrypted.decode())


def save_patients(patients):

    data = json.dumps(patients).encode()

    encrypted = cipher.encrypt(data)

    with open(DATA_FILE, "wb") as f:
        f.write(encrypted)



def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        return None



def handle(c):

    try:
        data = json.loads(c.recv(4096).decode())


        if "username" in data:

            u = data["username"]
            p = data["password"].encode()

            h = users.get(u)

            if not h or not bcrypt.checkpw(p, h):
                c.send(b'{"status":"fail"}')
                return

            token = jwt.encode(
                {"sub": u, "exp": int(time.time()) + 3600},
                SECRET,
                algorithm="HS256"
            )

            c.send(json.dumps({"token": token}).encode())
            return


        token = data.get("token")

        user = verify_token(token)

        if not user:
            c.send(b'{"status":"unauthorized"}')
            return

        action = data.get("action")

        if action == "create_patient":

            patients = load_patients()

            patient = data["data"]
            patient["id"] = len(patients) + 1
            patient["created_by"] = user
            patient["created_at"] = int(time.time())

            patients.append(patient)

            save_patients(patients)

            c.send(json.dumps({
                "status": "ok",
                "patient": patient
            }).encode())


        elif action == "list_patients":

            patients = load_patients()

            c.send(json.dumps({
                "status": "ok",
                "patients": patients
            }).encode())

        else:
            c.send(b'{"status":"unknown_action"}')

    finally:
        c.close()



context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain("cert.pem", "key.pem")

with socket.socket() as s:

    s.bind((HOST, PORT))
    s.listen()

    with context.wrap_socket(s, server_side=True) as ss:

        print("OpenChiro Secure Server Running on port", PORT)

        while True:
            client, addr = ss.accept()
            handle(client)