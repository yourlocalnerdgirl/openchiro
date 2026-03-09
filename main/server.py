import socket,ssl,json,time,os,bcrypt
from jose import jwt

HOST="0.0.0.0"
PORT=8000
SECRET=os.getenv("SKY2011","MAIN1")

users={"molly":bcrypt.hashpw(b"pass1234",bcrypt.gensalt())}

context=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain("cert.pem","key.pem")

def handle(c):
    try:
        data=json.loads(c.recv(1024).decode())
        u,p=data["username"],data["password"].encode()
        h=users.get(u)
        if not h or not bcrypt.checkpw(p,h):
            c.send(b'{"status":"fail"}')
            return
        t=jwt.encode({"sub":u,"exp":int(time.time())+3600},SECRET,"HS256")
        c.send(json.dumps({"token":t}).encode())
    finally:
        c.close()

with socket.socket() as s:
    s.bind((HOST,PORT))
    s.listen()
    with context.wrap_socket(s,server_side=True) as ss:
        while True:
            c,_=ss.accept()
            handle(c)