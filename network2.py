import pickle
import random
from GameControl.game_message import *
import struct
import socket
from Tiles.Bob.bob import *

class DATA_BOB:
    def __init__(self,nb_bob,list_bob_param,nb_food,list_food):
        self.nb_bob = nb_bob  # Numero de Bob
        self.bob_id = list_bob_param[0] # Identifiant de bob
        self.bob_coord = list_bob_param[1]
        self.velocity = list_bob_param[2]  # Vitesse de Bob
        self.mass = list_bob_param[3]  # Masse de Bob
        self.perception = list_bob_param[4]  # Perception de Bob
        self.nbfood = nb_food
        self.listfood = list_food

    def send(self,data,socket):
        data_send = pickle.dump(data)
        socket.sendall(data_send)
        print(f"Données envoyés dans paquet: {data}")

    def close(self):
        self.socket.close()

    
    # def assign_bob_to_player(self,id_player,list_bob):
    #     if (self.id_player == id_player):
    #         for self.bob in list_bob:
    #             self.id_second = self.id_player
    #     else:
    #         return
        
    
class Unite_de_controle:
    def __init__(self):
        self.type = 0
        self.port = 8080 #random.randint(8000,9000)
        self.size = 0
        self.data = []
        self.byte = b""
    
    def encodage(self):
        self.byte = struct.pack("B",self.type)
        self.byte = self.byte + struct.pack("I",self.port)
        self.byte = self.byte + struct.pack("I",self.size)
        self.byte = pickle.dumps(self.data)
        self.size = len(pickle.dumps(self.data))
        return self.byte
    
    def send_mess(self):
        global client_socket
        encoded_message =self.encodage()
        client_socket.sendall(encoded_message)
        print(f"Paquet envoyé: {encoded_message}")

    def create_mess(self,message_type,bob_data):
        self.type = message_type
        self.data.append(bob_data)
        print("Paquet crée")

    
    def update(self, message_decod):
        if (message_decod[0] == PYMSG_BOB_MOVE):
            bob_id, (new_x, new_y) = message_decod[10], message_decod[11]
            new_bob = Bob(bob_id,(new_x,new_y))
            for _ in range(message_decod[12]):
                new_bob.getCurrentTile()
                new_bob.determineNextTile()
                new_bob.move()











# if __name__ == "__main__":
    # new_msg = Message()
    # new_msg.type = gm.PYMSG_BOB_MOVE
    # bob_stat = [1,(2,3),25,30,45]
    # bob_data = DATA_BOB(1, bob_stat, 50, [])   
    # new_msg.data.append(bob_data)
    
    # bob_stat = [1,(2,3),25,30,45]
    # bob_data = DATA_BOB(1, bob_stat, 50, []) 
    # create_pack = mess.create_mess(PYMSG_BOB_MOVE,bob_data)
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect(('localhost', create_pack.port))
    #     create_pack.send(s)
    #     print("Message envoyé et connexion fermée")
    
    
    # new_msg = Message()
    # new_msg.type = gm.PYMSG_GAME_UPDATE
    # new_data = DATA_BOB()
    # new_msg.data.append(new_data)

    
    
    # data = DATA_BOB()
    # data(3,[1,(2,3),25,30,45],50)

