import sys
import socket
import threading
import tkinter as tk

from muuttujat import *

CLIENT_ADDR = "172.22.224.1"  # TODO: muuta tämä!


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
            # "BUFFER_SIZE" selitettynä: https://youtu.be/ORsYkznN7Ss?si=jnqRhuanSm7PLr8s
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
        print(f"Yritetään yhdistää; {CLIENT_ADDR}:{PORT}...")
        self.sock.connect((CLIENT_ADDR, PORT))

        # Yhdistäminen onnistui!
        print(f"Onnistuneesti yhdistetty; {CLIENT_ADDR}:{PORT}\n")
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

    def send(self, text_input):
        # Lähettää syötteen datan käyttöliittymän kautta.
        msg = text_input.get()
        text_input.delete(0, tk.END)
        self.messages.insert(tk.END, f'{self.name}: {msg}')

        # Kirjoita "exit" poistuaksesi chat-huoneesta.
        if msg == 'exit':
            self.sock.sendall(f"Palvelin: {self.name} on poistunut.".encode(ENCODING))
            # Poistutaan chatista.
            self.sock.close()
            sys.exit(0)
        else:
            # Lähetetään viesti normaalisti.
            self.sock.sendall(f"{self.name}: {msg}".encode(ENCODING))


def main():
    # Alustetaan ja ajetaan käyttöliittymä.
    client = Client()
    receive = client.start()

    # Käyttöliittymä.
    window = tk.Tk()
    window.title("Chat app")
    from_message = tk.Frame(master=window)
    scroll_bar = tk.Scrollbar(master=from_message)
    messages = tk.Listbox(master=from_message, yscrollcommand=scroll_bar.set)
    scroll_bar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Käyttöliittymän kautta asetetaan viestit.
    client.messages = messages
    receive.messages = messages

    # Asetellaan päänäkymä.
    from_message.grid(row=0, column=0, columnspan=2, sticky="nsew")
    from_entry = tk.Frame(master=window)
    text_input = tk.Entry(master=from_entry)
    text_input.pack(fill=tk.BOTH, expand=True)
    text_input.bind("<Return>", lambda x: client.send(text_input))
    text_input.insert(0, "")

    # Nappi, jota painamalla viesti lähetetään
    button_send = tk.Button(master=window, text="Lähetä", command=lambda: client.send(text_input))

    from_entry.grid(row=1, column=0, padx=10, sticky="ew")
    button_send.grid(row=1, column=1, pady=10, sticky="ew")

    # Ikkunan rakenne kuvataan seuraavilla riveillä:
    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    # Tärkein kooodi
    window.mainloop()



if __name__ == "__main__":
    main()


