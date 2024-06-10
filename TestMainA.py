

from Tiles.Bob.bob import Bob
from Network.Network import Network
from time import sleep


def main():
    ConnectionToC = Network(7000)
    ConnectionToC.openServerOnC()
    print("Connected")
    sleep(1)
    monBob = Bob()
    monBob.id=12345
    ConnectionToC.send(monBob)
    sleep(2)
    ConnectionToC.exit()

if __name__ == "__main__":
    main()

