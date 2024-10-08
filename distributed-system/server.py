import socket
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2] # listen for 1, send for 2
queue = Queue()
all_connections = []
all_addresses = []

def server():
    hostname = socket.gethostname()
    port = 8080

    server_socket = socket.socket()
    server_socket.bind((hostname, port))

    server_socket.listen(2)
    conn, addr = server_socket.accept()
    print('Got connection from', addr)
    while True:
        data = conn.recv(1024).decode() # utf-8
        if not data:
            break
        print('from connected user', data)
        data = input(' -> ')
        conn.send(data.encode())

    conn.close()

if __name__ == '__main__':
    server()

