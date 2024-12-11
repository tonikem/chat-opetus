import os
import socket
import argparse
import threading

from pymupdf import message

from muuttujat import *


class Server(threading.Thread):
    def __init__(self):
        super.__init__()
        self.connections = []

    def run(self):
        # Luodaan socket-olio "sock"
        # Ensimmäinen parametri (AF_INET) määrittää osoiteperheen.
        # Toinen parametri (SOCK_STREAM) tarkoittaa TCP-yhteyttä.
        # (SOCK_DGRAM tarkoittaisi UDP-yhteyttä)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Asetetaan socket-olion käyttö.
        # Ensimmäinen paramteri (SOL_SOCKET) tarkoittaa itse socket-yhteyttä.
        # Toinen parametri (SO_REUSEADDR) tarkoittaa sitä, että socketteja uusiokäytetään.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Kiinnitetään socket-olioon IP-osoite (HOST) ja portin numero (PORT).
        sock.bind((HOST, PORT))

        # Socket-olio asetetaan kuuntelemaan pyyntöä toiselta ohjelmalta.
        sock.listen(1)
        print("Listening at:", sock.getsockname())

        while True:
            # Otetaan vastaan uusi socket-yhteys
            sc, sockname = sock.accept()
            print(f"Uusi yhteys havaittu: {sc.getpeername()}, {sc.getsockname()}")

            # Luodaan uusi säie ja ajetaan se.
            server_socket = ServerSocket(sc, sockname, self)
            server_socket.start()

            # Lisätään socket-olio listaan
            self.connections.append(server_socket)

            print(f"Valmis ottamaan vastaan viestejä:", sc.getpeername())

    def broadcast(self, message, source):
        for connection in self.connections:
            # Tarkistetaan, ettei viestin vastaanottaja ole sama kuin lähettäjä.
            if connection.sockname != source:
                # Jos "sockname" on eri kuin "source", lähetetään viesti.
                connection.send(message)

    def remove_connection(self, connection):
        # Poistetaan yhteysolio listasta.
        self.connections.remove(connection)


class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server

    def run(self):
        while True:
            message = self.sc.recv(BUFFER_SIZE).decode('ascii')

            # Jos "message" löytyy, tulostetaan se näytölle ja lähetetään (broadcast) muille.
            if message:
                print(f"{self.sockname} lähetti viestin: {message}")
                self.server.broadcast(message, self.sockname)
            # Muussa tapauksessa tulostetaan ilmoitus.
            else:
                print(f"{self.sockname} on sulkenut yhteyden.")
                self.sc.close()
                self.server.remove_connection(self) # <- Tässä tarkkana:
                                                    # "self" viittaa itse palvelimen olioon,
                                                    # joka on tallennettu listaan "self.connections"

    def send(self, msg):
        self.sc.sendall(msg.encode('ascii'))

    def exit(self):
        while True:
            user_input = input("")
            if user_input == 'q':
                print("Suljetaan kaikki yhteydet")
                for connection in self.server.connections:
                    connection.sc.close()



