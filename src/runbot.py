import socket
import json
from time import sleep
from multiprocessing import Process, Queue, Event
from config import (consumer_key, consumer_secret,
                    access_token, access_token_secret,
                    rpc_user, rpc_password, rpc_port,
                    server_port)

def main():
    q = Queue()
    end_flag = Event()
    p = Process(target = runbot, args = (q, end_flag))

    p.start()

    with socket.socket() as s:
        s.bind(('localhost', server_port))
        s.listen(5)

        try:
            while True:
                conn, addr = s.accept()
                data = recv_data(conn)
                
                try:
                    data_json = json.loads(data)
                except json.decoder.JSONDecodeError:
                    continue

                q.put(data_json)
                conn.close()

        except KeyboardInterrupt:
            end_flag.set()
            p.join()

def runbot(q, end_flag):
    tipkoto = TipKoto()
    try:
        while True:
            if end_flag.is_set() and q.empty():
                break

            if q.empty():
                sleep(1)
                continue

            tipkoto.run(q.get())

    except KeyboardInterrupt:
        pass

def recv_data(conn):
    complete_data = b''
    while True:
        received_data = conn.recv(4096)
        if len(received_data) == 0:
            break

        complete_data += received_data

    return complete_data.decode()

if __name__ == '__main__':
    main()

