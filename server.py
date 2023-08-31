import socket
import logging
from bitstring import ConstBitStream
from time import time
from threading import Thread
from coords import *

class Server:

    def __init__(self):
        self.socket_servidor = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind_and_listen()
        self.accept_connections()
        self.conectado = True

    def bind_and_listen(self):
        host = socket.gethostname()
        self.socket_servidor.bind(("localhost", 10001))
        self.socket_servidor.listen(5)
        logging.info("Servidor escuchando en {}:{}...".format(
            "localhost", 10001))

    def accept_connections(self):
        thread = Thread(target=self.accept_connections_thread)
        thread.start()

    def accept_connections_thread(self):
        logging.info("Servidor aceptando conexiones...")
        while True:
            client_socket, _ = self.socket_servidor.accept()
            self.socket_cliente = client_socket
            listening_client_thread = Thread(
                target=self.listen_client_thread, args=(client_socket,), daemon=True)
            listening_client_thread.start()

    def listen_client_thread(self, client_socket):
        logging.info("Servidor conectado a un nuevo cliente...")

        while self.conectado:
            data0 = client_socket.recv(160)
            if data0:
                data = ConstBitStream(bytes=data0, length=160)

                msize = data.read('intle:16')
                mtype = data.read('intle:16')
                mtime = data.read('intle:64')

                # RA:
                ant_pos = data.bitpos
                ra = data.read('hex:32')
                data.bitpos = ant_pos
                ra_uint = data.read('uintle:32')

                # DEC:
                ant_pos = data.bitpos
                dec = data.read('hex:32')
                data.bitpos = ant_pos
                dec_int = data.read('intle:32')
                stell_pos=eCoords2str(ra_uint, dec_int, mtime)

                print(f"Received stellar object position: {stell_pos}")

if __name__ == "__main__":
    try:
        server = Server()
    except KeyboardInterrupt:
        logging.debug("Bye")
