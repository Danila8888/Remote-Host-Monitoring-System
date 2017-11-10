import socket
import sys
import pickle
import subprocess
import time
import os

SERVER = '192.168.0.107' #Server IP
CLIENT = '192.168.0.104' #Client IP
PORT = 50049 #OPEN PORT

def search_process(find_process):
    with open("log.txt", "a") as r:
        request_pidof = "pidof " + find_process
        try:
            stdoutdata_pidof = bytes.decode(
                subprocess.check_output(request_pidof, shell=True)).rstrip()  # request to get PID
        except:
            r.write(find_process + ";" + "not found" + ";" + "\n")
        stdoutdata = str(subprocess.check_output("ps -A", shell=True)).split("\\n")  # request to output all processes
        for i in range(len(stdoutdata)):
            process = stdoutdata[i].split(' ')[-1]
            if process == find_process:
                stdoutdata_pidof = bytes.decode(
                    subprocess.check_output(request_pidof, shell=True)).rstrip()  # request to get PID
                start_time = "ps -p " + stdoutdata_pidof + " -o lstart="
                stdoutdata_log = bytes.decode(subprocess.check_output(start_time, shell=True)).replace('\n',
                                                                                                       '')  # request to get start time
                user_name = "ps -p " + stdoutdata_pidof + " -o user="
                stdoutdata_name = bytes.decode(subprocess.check_output(user_name, shell=True)).replace('\n',
                                                                                                       '')  # request to get username
                r.write(find_process + ";" + stdoutdata_log + ";" + stdoutdata_name + "\n")
                request_pidof = None

soc = None
for res in socket.getaddrinfo(SERVER, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    af, socktype, proto, canonname, sa = res
    try:
        soc = socket.socket(af, socktype, proto)
    except OSError as msg:
        print(msg)
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
    print('could not open socket')
    sys.exit(1)
conn, addr = soc.accept()
with conn:
    print('Connected by', addr)
    while True:
        data = conn.recv(1024)
        if not data: break
        data_string = pickle.loads(data)
        config = []
        i = 0
        for element in data_string:
            config.append(data_string[i])
            i += 1
        conn.send(data)
        soc.close()
while (1):
    if os.path.exists("log.txt"):
        os.remove("log.txt")
    s = None
    for res in socket.getaddrinfo(CLIENT, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
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
        print('could not open socket')
        sys.exit(1)
    with s:
        i = 0
        for element in config:
            search_process(config[i])
            i += 1
        conf = []
        with open('log.txt', 'r') as f:
            conf = [row.strip() for row in f]
        data_string = pickle.dumps(conf)
        s.send(data_string)
        data_string = s.recv(1024)
        s.close()
    time.sleep(10)
