self.server_socket.listen(1)

    def accept_connections(self):
        thread = Thread(target=self.accept_connections_thread)
        thread.start()

    def accept_connections_thread(self):
        while True:
            client_socket, _ = self.server_socket.accept()
            with self.client_lock:
                self.client_socket = client_socket
            listening_client_thread = Thread(
                target=self.listen_client_thread, args=(client_socket,), daemon=True)
            listening_client_thread.start()

    def listen_client_thread(self, client_socket):
        logging.info("Server connected to a client...")
import socket
from PyQt5.QtCore import pyqtSignal, QObject
import logging
from bitstring import ConstBitStream
from time import time
from threading import Thread, Lock
import serial  # Import PySerial
from coords import *
from coords import radStr_2_deg, degStr_2_deg, rad_2_stellarium_protocol

class Server(QObject):
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind_and_listen()
        self.connected = True
        self.client_socket = None
        self.client_lock = Lock()

        # Initialize the Serial connection to the Arduino
        self.arduino = serial.Serial('COM12', 9600)  # Replace 'COM3' with the correct port
        self.arduino.timeout = 5  # Set a timeout for reading from Arduino

    def bind_and_listen(self):
        host = socket.gethostname()
        self.server_socket.bind(("localhost", 10001))
       
        while self.connected:
            data0 = client_socket.recv(160)
            if data0:
                data = ConstBitStream(bytes=data0, length=160)

                msize = data.read('intle:16')
                mtype = data.read('intle:16')
                mtime = data.read('intle:64')

                # RA:
                ant_pos = data.bitpos
                ra_str = data.read('hex:32')
                data.bitpos = ant_pos
                ra_uint = data.read('uintle:32')

                # DEC:
                ant_pos = data.bitpos
                dec_str = data.read('hex:32')
                data.bitpos = ant_pos
                dec_int = data.read('intle:32')



                sra,sdec,stime = eCoords2str(float("%f"%ra_uint), float("%f"%dec_int),float("%f"%mtime))
                dec_deg = degStr_2_deg(sdec)
                ra_deg = hourStr_2_deg(sra)



                # Send data to Arduino in the appropriate format
                ra_arduino, dec_arduino = float(ra_deg), float(dec_deg)
                arduino_data = f"{ra_arduino},{dec_arduino},\n"
                self.arduino.write(arduino_data.encode())
                response = self.arduino.readline().decode().strip()  # Read the response from the Arduino



                print(f"Received RA and DEC in degrees: {response}")

# The rest of your code...
if __name__ == "__main__":
    try:
        server = Server()
        server.accept_connections()
    except KeyboardInterrupt:
        logging.debug("Bye")
