import random
# from GameControl.settings import *
import matplotlib.pyplot as plt
from GameControl.setting import Setting
# from view.graph import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Tiles.Bob.bob import Bob
    # from Tiles.Food import Food
    from Tiles.tiles import Tile
from socket import gethostname, gethostbyname #Add
from random import randint #Add


class GameControl:
    instance = None
    #initialisation of grids:
    def __init__(self):
        # raise Exception("This class is a singleton!")
        self.setting = Setting.getSettings()
        self.grid : list[list['Tile']] = None
        self.nbBobs: 'int'= 0
        self.nbBobsSpawned = 0
        self.listBobs : list['Bob'] = []
        self.listOtherBobs : list['Bob'] = [] #Add
        self.listFoods: set['Tile'] = set()
        self.listOtherFoods : set['Tile'] = set() #Add

        self.newBornQueue : list['Bob'] = []
        self.diedQueue: list['Bob'] = []
        self.nbDied : 'int'= 0
        self.nbBorn : 'int'= 0
        self.currentTick = 0
        self.currentDay = 0
        self.renderTick = 0
############################ Graph Data ########################################        
        self.graphData = []
        self.diedData = []
        self.massData = []
        self.bornData = []
        self.veloceData = []
        self.energyData = []
        self.visionData = []
        self.toto_tick = 0        
        self.nbMass = 0
        self.nbVeloce = 0
        self.nbVision = 0
        self.nbEnergy = 0
        # self.graph = Graph()
################################# Graph methods ########################################
    def getMasses(self) -> list[float]:
        masses = [bob.getMass() for bob in self.getListBobs()]
        return masses
    
    def getVeloce(self) -> list[float]:
        veloce = [bob.getVelocity() for bob in self.getListBobs()]
        return veloce
    
    def getVision(self) -> list[float]:
        vision = [bob.getVision() for bob in self.getListBobs()]
        return vision
    
    def getEnergies(self) -> list[float]:
        energies = [bob.getEnergy() for bob in self.getListBobs()]
        return energies
##############################################################################################
    def updateMassData(self):
        masses = self.getMasses()
        masse_moyenne = sum(masses) / len(masses) if masses else 0
        self.nbMass = masse_moyenne
        self.massData.append((self.toto_tick, masse_moyenne))

    def updateVeloceData(self):
        veloce = self.getVeloce()
        veloce_moyenne = sum(veloce) / len(veloce) if veloce else 0
        self.nbVeloce = veloce_moyenne
        self.veloceData.append((self.toto_tick, veloce_moyenne))

    def updateVisionData(self):
        vision = self.getVision()
        vision_moyenne = sum(vision) / len(vision) if vision else 0
        self.nbVision = vision_moyenne
        self.visionData.append((self.toto_tick, vision_moyenne))

    def updateEnergyData(self):
        energies = self.getEnergies()
        energy_moyenne = sum(energies) / len(energies) if energies else 0
        self.nbEnergy = energy_moyenne
        self.energyData.append((self.toto_tick, energy_moyenne))
#######################################################################################
    def initiateGame(self):
        self.setting = Setting.getSettings()
        self.grid : list[list['Tile']] = None
        self.nbBobs: 'int'= 0
        self.nbBobsSpawned = 0
        self.listBobs : list['Bob'] = []
        self.listOtherBobs : list['Bob'] = [] #Add
        self.listFoods: set['Tile'] = set()
        self.listOtherFoods: set['Tile'] = set()
        self.newBornQueue : list['Bob'] = []
        self.diedQueue: list['Bob'] = []
        self.currentTick = 0
        self.currentDay = 0
        self.renderTick = 0
############################ Graph Data ########################################
        self.graphData = []
        self.diedData = []
        self.massData = []
        self.bornData = []
        self.veloceData = []
        self.energyData = []
        self.visionData = []
        self.toto_tick = 0        
        self.nbMass = 0
        self.nbVeloce = 0
        self.nbVision = 0
        self.nbEnergy = 0

    def setMap(self, map):
        self.grid = map
    def getMap(self):
        return self.grid
    def getNbBobs(self):
        return self.nbBobs
    def setNbBobs(self, nbBobs):
        self.nbBobs = nbBobs
    def getNbBorn(self):
        return self.nbBorn
    def setNbBorn(self, nbBorn):
        self.nbBorn = nbBorn
    def getNbDied(self):
        return self.nbDied
    def setNbDied(self, nbDied):
        self.nbDied = nbDied
    def getNbMass(self):
        return self.nbMass
    def setNbMass(self, nbMass):
        self.nbMass = nbMass
    def getListBobs(self):
        return self.listBobs
    def getNbBobsSpawned(self):
        return self.nbBobsSpawned
    def setNbBobsSpawned(self, nbBobsSpawned):
        self.nbBobsSpawned = nbBobsSpawned
    def getNewBornQueue(self):
        return self.newBornQueue
    def getFoodTiles(self) -> list['Tile']:
        foodTiles = []
        for row in self.getMap():
            for tile in row:
                if tile.getEnergy() > 0:
                    foodTiles.append(tile)
        return foodTiles
    
    def getOtherTiles(self) -> list['Tile']:
        otherTiles = []
        for row in self.getMap():
            for tile in row:
                if tile.getEnergy() == 0:
                    otherTiles.append(tile)
        return otherTiles

    def initiateBobs(self, nbBobs):
        from Tiles.Bob.bob import Bob
        for _ in range(nbBobs):
            print("Adding bob")
            x = random.randint(0, self.setting.getGridLength() - 1)
            y = random.randint(0, self.setting.getGridLength() - 1)
            tile = self.getMap()[x][y]
            bob = Bob()
            bob.spawn(tile)
        # self.pushToList()
    #########################################  Fonction ajoutées par florine et celestine Add
    def initiateOtherBobs(self, listOtherBobs): #in the future, will be used for initiating the bobs of other players
        from Tiles.Bob.bob import Bob
        for otherBob in listOtherBobs:
            print("Adding other bob")
            x = otherBob.CurrentTile.gridX
            y = otherBob.CurrentTile.gridY
            tile = self.getMap()[x][y]
            otherBob.isMine = False
            otherBob.spawnOtherBob(tile)
            
    def clearOtherBobs(self, listOtherBobs):
        from Tiles.Bob.bob import Bob
        for bob in listOtherBobs:
            ###to do : il faudra surement ajouter un sécurité pour ne pas qu'on ai un probleme si on tombe sur un bob qui c'est fait mangé
            bob.CurrentTile.removeBob(bob)
            indexBob = self.listOtherBobs.index(bob)
            del self.listOtherBobs[indexBob] #On enleve le bob de listOtherBobs, attention je crois que Phuc lui laisse les bobs morts dans la liste mais juste les ajoute au mort ou jsp, a verifier
    #########################################################################################"


    
    def eatingTest(self):
        from Tiles.Bob.bob import Bob
        x1 = random.randint(0, self.setting.getGridLength() - 1)
        y1 = random.randint(0, self.setting.getGridLength() - 1)
        tile1 = self.getMap()[x1][y1]
        bob1 = Bob()
        bob1.spawn(tile1)
        bob1.mass = 2
        bob1.velocity = 1.5
        x2 = random.randint(0, self.setting.getGridLength() - 1)
        y2 = random.randint(0, self.setting.getGridLength() - 1)
        tile2 = self.getMap()[x2][y2]
        bob2 = Bob()
        bob2.spawn(tile2)
        bob2.mass = 1
        bob2.velocity = 1
        x3 = random.randint(0, self.setting.getGridLength() - 1)
        y3 = random.randint(0, self.setting.getGridLength() - 1)
        tile3 = self.getMap()[x3][y3]
        bob3 = Bob()
        bob3.spawn(tile3)
        bob3.mass = 4
        bob3.velocity = 2
        # self.pushToList()


    def pushToList(self):
        for bob in self.newBornQueue:
            self.listBobs.append(bob)
            self.nbBobs += 1
            self.nbBobsSpawned += 1
        self.newBornQueue.clear()

    def addToNewBornQueue(self, bob: 'Bob'):
        self.newBornQueue.append(bob)
        self.nbBorn +=1
    def addToDiedQueue(self, bob: 'Bob'):
        self.diedQueue.append(bob)

    def wipeBobs(self):
        for bob in self.diedQueue:
            self.listBobs.remove(bob)
            self.nbBobs -= 1
            self.nbDied += 1
        self.diedQueue.clear()

    def createWorld(self, lengthX, lengthY ):
        from Tiles.tiles import Tile 
        world = []
        for i in range(lengthX):
                world.append([])
                for j in range(lengthY):
                    tile = Tile(gridX=i,gridY= j)
                    
                    world[i].append(tile)
        self.setMap(world)
    
    def wipeFood(self):
        # for row in self.getInstance().getMap():
        #     for tile in row:
        for tile in self.listFoods:
            # if tile.getEnergy() == FOOD_ENERGY:
            tile.removeFood()
        self.listFoods.clear()

    def respawnFood(self):
        # couples: list[tuple] = []
        for _ in range(self.setting.getNbSpawnFood()):
            x = random.randint(0,self.setting.getGridLength()-1)
            y = random.randint(0,self.setting.getGridLength()-1)
            # while (x, y) in couples:
            #     x = random.randint(0,self.setting.getGridLength()-1)
            #     y = random.randint(0,self.setting.getGridLength()-1)
            self.getMap()[x][y].spawnFood()
            self.listFoods.add(self.getMap()[x][y])
            # couples.append((x, y))
    #########################################  Fonction ajoutées par florine et celestine Add
    def initiateOtherBobs(self, listOtherBobs): #in the future, will be used for initiating the bobs of other players
        from Tiles.Bob.bob import Bob
        for otherBob in listOtherBobs:
            print("Adding other bob")
            x = otherBob.CurrentTile.gridX
            y = otherBob.CurrentTile.gridY
            tile = self.getMap()[x][y]
            otherBob.isMine = False
            otherBob.spawnOtherBob(tile)

    ####################### Add to show other's foods
    def wipeOtherFood(self): #A faire à chaque tik au lieu de chaque day
        for tile in self.listOtherFoods:
            tile.removeFood()
        self.listOtherFoods.clear()
    def respawnOtherFood(self, dictionaryOtherFoods):
        for coord in dictionaryOtherFoods: #On a un dictionnaire coord(x,y) : energie (coord un tuple et energie un float)
            x = coord[0]
            y = coord[1]
            print("x,y :", x,y)
            print(self.grid[x][y])
            foodEnergy = dictionaryOtherFoods[coord]
            self.grid[x][y]
            self.getMap()[x][y].spawnOtherFood(foodEnergy) #le paramètre doit être un entier
            #PROBLEME POTENTIEL : la listOtherFoods contient les cases chez l'autre joueur, jsp si ça vas fonctionner comme ça pour l'affichage
            self.listOtherFoods.add(self.getMap()[x][y]) #Pas besoin de l'ajouter a la liste
    ########################

            
    def clearOtherBobs(self, listOtherBobs):
        from Tiles.Bob.bob import Bob
        for bob in listOtherBobs:
            ###to do : il faudra surement ajouter un sécurité pour ne pas qu'on ai un probleme si on tombe sur un bob qui c'est fait mangé
            bob.CurrentTile.removeBob(bob)
            indexBob = self.listOtherBobs.index(bob)
            del self.listOtherBobs[indexBob] #On enleve le bob de listOtherBobs, attention je crois que Phuc lui laisse les bobs morts dans la liste mais juste les ajoute au mort ou jsp, a verifier
    #########################################################################################"


    def updateRenderTick(self):
        self.renderTick += 1
        if self.renderTick == self.setting.getFps():
            self.renderTick = 0
            self.increaseTick()
        

    def increaseTick(self):

        for x in self.grid:
            for tile in x:
                tile.seen = False
        self.bornData.append((self.toto_tick,self.nbBorn))
        self.nbBorn = 0
        self.pushToList()
        self.wipeBobs()


        #Avant de mettre a jour la liste des bob des autres 
        #On nettoie pour pas avoir plusieurs fois les others bobs et la nourriture
        if(self.listOtherBobs): #if a supprimer je pense
            self.clearOtherBobs(self.listOtherBobs)
        self.wipeOtherFood()
        ####################################  RECUPERER ICI LA LISTE DES BOBS TRANSMISE PAR LES AUTRES ET DES NOURRITURES #####
        #dictionaryOtherFoods = # ce que les autre les nous envoie
        ####################################  il faudra aussi gerer le fait que les autres puissent affecter nos propres bobs #
        #dans le but de tester : Add
        from Tiles.Bob.bob import Bob
        from Tiles.tiles import Tile

        bob1 = Bob()
        bob1.id = 99999999
        bob1.CurrentTile = Tile(randint(1,10),3)
        #bob1.CurrentTile.addBob(bob1)
        self.listOtherBobs.append(bob1)

        dictionaryOtherFoods = {(4,5):100, (7,10):30}
        ##############

        self.initiateOtherBobs(self.listOtherBobs) #Add, met les bobs dans les cases
        self.respawnOtherFood(dictionaryOtherFoods)

        self.listBobs.sort(key=lambda x: x.speed, reverse=True)
        for bob in self.listBobs:
            bob.clearPreviousTiles()
        for bob in self.listBobs:
            if bob not in self.diedQueue:
             ########################################################################### 
                #Add : Vérification que le bob qui va être bougé appartient bien au joueur
                #Si on parcours tous les bobs et pas juste les notres, il faudrait mettre ce test avant not in sel.died Queue pour optimiser
                if bob.ipOwner == gethostbyname(gethostname()):
                    #print(bob.id) #Add debuggage
                    bob.action()
        # for bob in self.listBobs:
        #     if bob not in self.diedQueue:
                
        self.currentTick += 1
        self.graphData.append((self.toto_tick,self.nbBobs)) 
        self.diedData.append((self.toto_tick,self.nbDied))
        self.nbDied = 0
        self.massData.append((self.toto_tick,self.nbMass))
        self.veloceData.append((self.toto_tick,self.nbVeloce))
        self.visionData.append((self.toto_tick,self.nbVision))
        self.energyData.append((self.toto_tick,self.nbEnergy))
        self.updateEnergyData()
        self.updateMassData()
        self.updateVeloceData()
        self.updateVisionData()
        self.toto_tick +=1
        if self.currentTick == self.setting.getTicksPerDay():
            self.currentTick = 0
            self.increaseDay()
                ##### Add : Ajout pour envoyer ce qu'on a fait aux autres joueurs
        ################# a decommenter quand ça aura été testé :
        #Pour la bouffe
        #dictionaryOtherFoodsToSend = {}
        #dictionaryMyFoodsToSend = {}
        #for tile in self.listOtherFoods:
            #coord = (tile.gridX, tile.gridY)
            #dictionaryOtherFoodsToSend[coord] = tile.foodEnergy
        #for tile in self.listFoods:
            #coord = (tile.gridX, tile.gridY)
            #dictionaryMyFoodsToSend[coord] = tile.foodEnergy
        # At the end of the tick, we have listBob, newBornQueue, diedQueue
        
    def increaseDay(self):
        self.wipeFood()
        self.respawnFood()
        self.currentDay += 1
        self.graphData.append((self.toto_tick,self.nbBobs))
        self.diedData.append((self.toto_tick,self.nbDied))
        self.diedData.append((self.toto_tick,self.nbMass))
        self.bornData.append((self.toto_tick,self.nbBorn))
        self.veloceData.append((self.toto_tick,self.nbVeloce))



    def getRenderTick(self):
        return self.renderTick
    def getTick(self):
        return self.currentTick
    def setTick(self, tick):
        self.currentTick = tick
    def getDay(self):
        return self.currentDay
    def setDay(self, day):
        self.currentDay = day
    def getDiedQueue(self):
        return self.diedQueue


    @staticmethod
    def  getInstance():
        if GameControl.instance is None:
            if (GameControl.instance is not None):
                raise Exception("This class is a singleton!")
            GameControl.instance = GameControl()
        return GameControl.instance

    # def update():




