import socket
import sys
import pickle
import time

SERVER = '192.168.0.107' #SERVER IP
CLIENT = '192.168.0.104' #CLIENT IP
PORT = 50049 #OPEN PORT

s = None
for res in socket.getaddrinfo(SERVER, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except OSError as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except OSError as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print('Could not open socket')
    sys.exit(1)
with s:
    conf = []
    with open('conf.txt', 'r') as f:
        conf = [row.strip() for row in f]
    data_string = pickle.dumps(conf)
    s.send(data_string)
    data_string = s.recv(1024)
    s.close()

while(1):
    soc = None
    for res in socket.getaddrinfo(CLIENT, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            soc = socket.socket(af, socktype, proto)
        except OSError as msg:
            soc = None
            continue
        try:
            soc.bind(sa)
            soc.listen(1)
        except OSError as msg:
            soc.close()
            soc = None
            continue
        break
    if soc is None:
        print('Could not open socket')
        sys.exit(1)
    conn, addr = soc.accept()
    print('Connected by', addr)
    with conn:
        while True:
            data = conn.recv(1024)
            if not data: break
            data_string = pickle.loads(data)
            print("%10s%30s%10s" % ("NAME", "DATE", "USER"))
            conf = []
            i = 0
            for element in data_string:
                pr = data_string[i]
                pr = pr.split(";")
                print("%10s%30s%10s" % (pr[0], pr[1], pr[2]))
                i += 1
            conn.send(data)
            soc.close()
    time.sleep(10)
