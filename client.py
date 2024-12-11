import sys
import socket
import threading
import tkinter as tk
from platform import system

from adbutils.pidcat import message

from muuttujat import *


class Send(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        # Kuuntelee käyttäjän input-arvoja.
        # Kirjoita "exit" sulkeaksesi yhteyden.
        while True:
            print(f"{self.name}: ", end='')
            sys.stdout.flush()
            # "flush()" puskee kaikki puskurin sisältämät merkit/merkkijonot terminaaliin vaikka normaalisti sitä joutuisi odottamaan.
            # Lisätietoa flush-metodista ja puskurista: https://realpython.com/python-flush-print-output

            # Luetaan rivi merkkejä, joita stdin on ottanut vastaan.
            msg = sys.stdin.readline().strip()

            if msg == "exit":
                # Suljetaan yhteys.
                self.sock.sendall(f"Palvelin {self.name} on poistunut.".encode(ENCODING))
                break
            else:
                # Lähetetään viesti.
                self.sock.sendall(f"{self.name}: {msg}".encode(ENCODING))

        print("\nSuljetaan yhteys...")
        self.sock.close()
        sys.exit(0)


class Receive(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = []

    def run(self):
        while True:
            msg = self.sock.recv(BUFFER_SIZE).decode(ENCODING)
            if msg:
                if self.messages:
                    self.messages.insert(tk.END, msg)
                    print(f"\r{msg}\n{self.name}: ", end='')
                else:
                    print(f"\r{msg}\n{self.name}: ", end='')
            else:
                print(f"\nYhteys palvelimeen kadotettu!")
                self.sock.close()
                sys.exit(1)


class Client:
    def __init__(self):
        # Taas alustetaan socket-olio
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = []

    def start(self):
        # Katsotaan onnistuuko yhdistäminen..
        print(f"Yritetään yhdistää; {HOST}:{PORT}...")
        self.sock.connect((HOST, PORT))

        # Yhdistäminen onnistui!
        print(f"Onnistuneesti yhdistetty; {HOST}:{PORT}\n")
        self.name = input("Anna nimesi: ")
        print()
        print(f"Tervetuloa {self.name}!")

        # Luodaan send- ja recieve-säikeet:
        send = Send(self.sock, self.name)
        receive = Receive(self.sock, self.name)

        send.start()
        receive.start()

        self.sock.sendall(f"Server: {self.name} on liittynyt chattiin.".encode(ENCODING))
        print("\rKaikki valmiina. Poistu chat-huoneesta kirjoittamalla \"exit\"")
        return receive


if __name__ == "__main__":


