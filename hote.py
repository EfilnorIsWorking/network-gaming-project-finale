import socket
from GameControl.network2 import *
from GameControl.EventManager import *
import subprocess


class HOTE:
    def __init__(self):
        self.server_socket = 0
        self.client_socket = 0

    def listen_python(self):

        adress_host = '0.0.0.0'  # Accepter les connexions de toutes les adresses IP
        port = 8080       # Port sur lequel le serveur écoute

        self.host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.host_socket.bind((adress_host, port))
        self.host_socket.listen(5)

        print(f"Hote en écoute sur le port {port}...")
        return self.host_socket

    def run_c(self):
        etat = EtatJeu.getEtatJeuInstance()
        executable_path="./GameControl/client"
        if not os.path.exists(executable_path):
            print("Client not found")
            etat.kill()
            return
        subprocess.Popen(executable_path)

    def accept_python(self):
        # Attente d'une connexion
        self.client_socket, client_address = self.server_socket.accept()
        # client_socket.sendall('aosnfiakdnfofi')
        print(f"Connexion acceptée de {client_address}")

        # Réception des données
        data = self.client_socket.recv(1024).decode('utf-8')
        print(f"Données reçues : {data}")

        # Fermeture des sockets
        # client_socket.close()
        # server_socket.close()

    
    def send_mess(self, mess):
        encoded_message =mess.encodage()
        self.client_socket.sendall(encoded_message)
        print(f"Paquet envoyé: {encoded_message}")

    def update(self, message_decod):
        if (message_decod[0] == PYMSG_BOB_MOVE):
            bob_id, (new_x, new_y) = message_decod[10], message_decod[11]
            new_bob = Bob(bob_id,(new_x,new_y))
            for _ in range(message_decod[12]):
                new_bob.getCurrentTile()
                new_bob.determineNextTile()
                new_bob.move()


    def receive_mess(self):
        # Lire les 9 premiers octets pour obtenir le type, le port et la taille des données
        self.client_socket.setblocking(0)
        header=b''
        try:
            header = self.client_socket.recv(9)
            if header == b'':
                return
        except BlockingIOError:
            return
        
        self.client_socket.setblocking(1)

        if len(header) < 9:
            raise ValueError("Paquet incomplet reçu")
        
        print("Commence par décoder")
        self.type, = struct.unpack("B", header[:1])
        self.port, = struct.unpack("I", header[1:5])
        self.size, = struct.unpack("I", header[5:9])
        print("Paquet décodé par octet")
        

        serialized_data = self.client_socket.recv(self.size)
        if len(serialized_data) < self.size:
            raise ValueError("Données incomplètes reçues")
    
        print(f"Serialized data reçu: {serialized_data}")

        
        print("Paquet décodé completement")
        self.byte = header + serialized_data
        self.data = pickle.loads(serialized_data)
        
        print(f"Paquet reçu: Type: {self.type}, Port: {self.port}, Taille: {self.size}, Données: {self.data}")
        return self.type, self.port, self.size, self.data
