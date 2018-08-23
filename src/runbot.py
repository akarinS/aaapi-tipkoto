import socket
from multiprocessing import Process, Queue, Event
import time
import json
from config import (consumer_key, consumer_secret,
                    access_token, access_token_secret,
                    rpc_user, rpc_password, rpc_port)
                    #server_port)

def main():
    print('main')
    q = Queue()
    end_flag = Event()
    p = Process(target = runbot, args = (q, end_flag))

    p.start()

    with socket.socket() as s:
        s.bind(('localhost', 8888))
        s.listen(5)

        try:
            while True:
                print('connect')
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
    print('runbot')
    #tipkoto = TipKoto()
    try:
        while True:
            print('in while')
            if end_flag.is_set() and q.empty():
                break

            if q.empty():
                print('waiting')
                time.sleep(1)
                continue

            #tipkoto.run(q.get())
            print(q.get())

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

