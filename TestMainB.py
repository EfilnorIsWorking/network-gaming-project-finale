
from Tiles.Bob.bob import Bob
from Network.Network import Network
import time

def main():
    ConnectionToC = Network(8000)
    ConnectionToC.connectToServerOnC("192.168.1.40")
    print("Connected")
    startTime=time.time()
    lastSendTime=time.time()
    mesBobs = []
    while time.time()-startTime<10 :
        tmp=ConnectionToC.recieve()
        if isinstance(tmp, Bob):
            mesBobs.append(tmp)
    for bob in mesBobs:
        print(bob.id)
    ConnectionToC.exit()

if __name__ == "__main__":
    main()

