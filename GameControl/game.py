from __future__ import annotations
from typing import TYPE_CHECKING
import pygame as pg
import sys
import socket
import time

import json

import threading  # 导入 threading 模块

# from GameControl.gameControl import GameControl
# from GameControl.settings import *
from GameControl.setting import Setting
from view.utils import draw_text
from view.camera import Camera
from view.world import World
# from GameControl.settings import *
# import random
from GameControl.EventManager import *
from GameControl.gameControl import GameControl
from GameControl.saveAndLoad import *
from view.graph import *
# from GameControl.inputManager import *

class Game:
    instance = None
    def __init__(self, screen, clock):
        self.setting = Setting.getSettings()
        self.gameController = GameControl.getInstance()
        self.screen = screen
        self.clock = clock
        self.width, self.height = self.screen.get_size()
        # self.gameController.createWorld(self.setting.getGridLength(),self.setting.getGridLength()) 
        self.world = None
        self.camera = None

        self.is_first_gamer = True

        self.server_connected = False
        self.client_connected = False

        # self.gameController.initiateBobs(self.setting.getNbBob())
        # # self.gameController.eatingTest()
        # self.gameController.respawnFood()
        # self.createNewGame()
        # print("Game: ", self.setting.getGridLength(), self.setting.getNbBob(), self.setting.getFps(), self.setting.getTileSize()) 
    
    def createNewGame(self):
        self.gameController.initiateGame()
        self.gameController.createWorld(self.setting.getGridLength(),self.setting.getGridLength()) 
        self.world = World(self.width, self.height)
        self.camera = Camera(self.width, self.height) 
        self.gameController.initiateBobs(self.setting.getNbBob())
        # self.gameController.eatingTest()
        self.gameController.respawnFood()
    
    def loadGame(self, saveNumber):
        loadSetting(saveNumber)
        # self.setting = Setting.getSettings()
        self.gameController.initiateGame()
        self.gameController.createWorld(self.setting.getGridLength(),self.setting.getGridLength()) 
        loadGameController(saveNumber)
        self.world = World(self.width, self.height)
        self.camera = Camera(self.width, self.height) 
        # self.gameController.initiateBobs(self.setting.getNbBob())
        loadBob(saveNumber)
        loadFood(saveNumber) 

    def saveGameByInput(self, event):
        if event.key == pg.K_1:
            # print("save")
            saveGame(1)
        if event.key == pg.K_2:
            # print("save")
            saveGame(2)
        if event.key == pg.K_3:
            # print("save")
            saveGame(3)
        if event.key == pg.K_4:
            # print("save")
            saveGame(4)
        if event.key == pg.K_5:
            # print("save")
            saveGame(5)

    
    


    

    def loadreseaux(self):
        gameController = GameControl.getInstance()

        

        with open("GameControl/testdata1.json", 'r') as file:
            data = json.load(file)
            #gameControl.clearOtherBobs(gameControl.listOtherBobs)
            gameControl.listOtherBobs.clear()

            for bob_data in data["bobs"]:
                bob = Bob()
                bob.setId(bob_data["id"])
                bob.setCurrentTile(gameController.getMap()[bob_data["x"]][bob_data["y"]])
                #bob.PreviousTiles.append(bob.CurrentTile)
                # bob.CurrentTile.addBob(bob)
                bob.setEnergy(bob_data["energy"])
                bob.setMass(bob_data["mass"])
                bob.setVelocity(bob_data["velocity"])
                bob.setVision(bob_data["vision"])
                bob.setMemoryPoint(bob_data["memoryPoint"])
                #bob.determineNextTile()
                gameController.getListOtherBobs().append(bob)
                # gameController.setNbBobs(gameController.getNbBobs() + 1)
                # gameController.setNbBobsSpawned(gameController.getNbBobsSpawned() + 1)

            # for bob_data in data["new_borns"]:
            #     bob = Bob()
            #     bob.setId(bob_data["id"])
            #     bob.setCurrentTile(gameController.getMap()[bob_data["x"]][bob_data["y"]])
            #     bob.setPreviousTile(bob.CurrentTile)
            #     bob.PreviousTiles.append(bob.CurrentTile)
            #     bob.CurrentTile.addBob(bob)
            #     bob.setEnergy(bob_data["energy"])
            #     bob.setMass(bob_data["mass"])
            #     bob.setVelocity(bob_data["velocity"])
            #     bob.setVision(bob_data["vision"])
            #     bob.setMemoryPoint(bob_data["memoryPoint"])
            #     bob.determineNextTile()
            #     gameController.addToNewBornQueue(bob)

            for food_data in data["foods"]:
                tile = gameController.getMap()[food_data["x"]][food_data["y"]]
                tile.foodEnergy = food_data["energy"]


    def savereseaux(self):
        print("save")
        
        data = {
            "bobs": [],
            # "new_borns": [],
            "foods": []
        }


        for bob in gameController.getListBobs():
            bob_data = {
                "id": bob.getId(),
                "x": bob.getCurrentTile().gridX,
                "y": bob.getCurrentTile().gridY,
                "energy": bob.getEnergy(),
                "mass": bob.getMass(),
                "velocity": bob.getVelocity(),
                "vision": bob.getVision(),
                "memoryPoint": bob.getMemoryPoint()
            }
            data["bobs"].append(bob_data)
            
        # for bob in gameController.getNewBornQueue():
        #     bob_data = {
        #         "id": bob.getId(),
        #         "x": bob.getCurrentTile().gridX,
        #         "y": bob.getCurrentTile().gridY,
        #         "energy": bob.getEnergy(),
        #         "mass": bob.getMass(),
        #         "velocity": bob.getVelocity(),
        #         "vision": bob.getVision(),
        #         "memoryPoint": bob.getMemoryPoint()
        #     }
        #     data["new_borns"].append(bob_data)
        
        for tile in gameController.getFoodTiles():
            if tile.foodEnergy > 0:
                food_data = {
                    "x": tile.gridX,
                    "y": tile.gridY,
                    "energy": tile.getEnergy()
                }
                data["foods"].append(food_data)
        
        with open("GameControl/testdata.json", "w") as file:
            json.dump(data, file, indent=4)


    def receive_server(self):
        receive_filename = 'GameControl/testdata1.json'
        # server_ip = "192.168.43.91"
        server_ip = "127.0.0.1"
        port = 8080

        # 创建一个TCP/IP套接字
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定套接字到端口
        server_socket.bind((server_ip, port))
        # 监听传入的连接
        server_socket.listen(1)

        print("等待连接...")
        connection, client_address = server_socket.accept()

        # 当连接建立时，将self.server_connected设置为True
        self.server_connected = True


        while True:
            # 接收文件数据
            time.sleep(1)
            with open(receive_filename, 'wb') as f:
                    data = connection.recv(10240)
                    if not data:
                        break
                    f.write(data)

            print(f"从客户端接收的文件已保存为：{receive_filename}")

    def send_client(self):
        # server_ip = "192.168.43.92"
        # port = 8080
        server_ip = "127.0.0.1"
        port = 8090  # Convert port to an integer
        send_filename = "GameControl/testdata.json"

        # Create a TCP/IP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        client_socket.connect((server_ip, port))
        while True:
            # Send file data
            with open(send_filename, 'rb') as f:
                data = f.read()
                client_socket.sendall(data)
            print(f"文件 {send_filename} 发送完毕。")
            time.sleep(1)
            

    def run(self):
        etat = EtatJeu.getEtatJeuInstance()
        self.playing = True
        tick_count = 0
        send_result = False
        server_running = True  # 控制服务器线程是否运行的标志

        # 启动服务器线程
        server_thread = threading.Thread(target=self.receive_server)
        server_thread.start()

        # client_thread = threading.Thread(target=self.send_client)
        # client_thread.start()

        while self.playing:

            if self.server_connected :
                if not self.client_connected:
                    client_thread = threading.Thread(target=self.send_client)
                    client_thread.start()
                    self.client_connected=True

            self.clock.tick(10)
            if tick_count%10 == 0 and tick_count>=10:
                try:
                    self.loadreseaux()
                except Exception as e:
                    print(f"加载数据时出错: {e}")

            self.events()
            self.update()
            
            if self.setting.simuMode:
                self.gameController.increaseTick()
                self.drawSimu()
            else:
                self.gameController.updateRenderTick()
                self.draw()

            tick_count += 1
            #gameControl.clearOtherBobs(gameControl.listOtherBobs)
            if tick_count%10 == 0 and tick_count>=10:
                try:
                    self.savereseaux()
                except Exception as e:
                    print(f"保存数据时出错: {e}")


            

        # 停止服务器线程
        server_running = False
        server_thread.join()  # 等待线程结束后继续

        

    def events(self):
        etat = EtatJeu.getEtatJeuInstance()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_g:
                    self.gameController.renderTick = 0
                    #graph methods
                    save_graph_data()
                    save_born_data()
                    save_died_data()
                    save_mass_data()
                    save_veloce_data()
                    save_vision_data()
                    save_energy_data()

                    show_graph_data()
                    show_born_data()
                    show_died_data()
                    show_mass_data()
                    show_veloce_data()
                    show_vision_data()
                    show_energy_data()
                    #graph methods
                if event.key == pg.K_m:
                    # i = show_menu(self.screen, self.clock)
                    # if i == 0:
                    #     self.createNewGame()
                    # else:
                    #     self.loadGame(i)
                    self.playing = False
                    etat.playing = False
                    etat.open_menu = True
                self.saveGameByInput(event)
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                if event.key == pg.K_BACKSPACE:
                    self.gameController.renderTick = 0
                    openIngamesetting()
                if event.key == pg.K_SPACE:
                    self.gameController.renderTick = 0
                    res = pause(self.screen,self.camera)
                    self.setting.simuMode = False
                    self.modeTransition(res)
                if event.key == pg.K_s:
                    self.gameController.renderTick = 0
                    self.setting.simuMode = not self.setting.simuMode
                if event.key == pg.K_r:
                    self.gameController.renderTick = 0
                    newObjectMenu(self.screen, self.clock ,self.camera)
    def update(self):
        self.camera.update()
        
    def drawSimu(self):
        self.screen.fill((137, 207, 240))
        self.world.drawSimu(self.screen, self.camera)
        self.drawIndex()
        pg.display.flip()


    def draw(self):
        self.screen.fill((137, 207, 240))
        self.world.draw(self.screen, self.camera)
        self.drawIndex()
        pg.display.flip()

    def drawIndex( self ):
        draw_text(
            self.screen,
            'FPS: {}'.format(round(self.clock.get_fps())),
            25,
            (0,0,0),
            (10, 10)
        )  
        draw_text(
            self.screen,
            'Tick: {}'.format(round(self.gameController.getTick())),
            25,
            (0,0,0),
            (10, 30)
        )  
        draw_text(
            self.screen,
            'Day: {}'.format(round(self.gameController.getDay())),
            25,
            (0,0,0),
            (10, 50)
        )  
        draw_text(
            self.screen,
            'Number of bobs: {}'.format(self.gameController.getNbBobs()) ,
            25,
            (0,0,0),
            (10, 70)
        )
        draw_text(
            self.screen,
            'Number of bob spawned: {}'.format(self.gameController.getNbBobsSpawned()) ,
            25,
            (0,0,0),
            (10, 90)
        )

    def saveGameByInput(self, event):
        if event.key == pg.K_1:
            # print("save")
            saveGame(1)
        if event.key == pg.K_2:
            # print("save")
            saveGame(2)
        if event.key == pg.K_3:
            # print("save")
            saveGame(3)
        if event.key == pg.K_4:
            # print("save")
            saveGame(4)
        if event.key == pg.K_5:
            # print("save")
            saveGame(5)
    
    def modeTransition(self, mode):
        if mode == 'Menu':
            i = show_menu(self.screen, self.clock)
            if i == 0:
                # print("i = ", i )
                # print("new game")
                self.createNewGame()
            else:
                self.loadGame(i)
        elif mode == 'InGameSetting':
            openIngamesetting()
        else:
            return


    @staticmethod
    def getInstance(screen, clock):
        if Game.instance == None:
            Game.instance = Game(screen, clock)
        return Game.instance


def send_and_receive_file(server_ip, port):
    send_filename = 'save/save2.txt'
    receive_filename = 'save/save2.txt'

    # 创建一个TCP/IP套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接到服务器
    client_socket.connect((server_ip, port))

    while(1):
        # 发送文件数据
        with open(send_filename, 'rb') as f:
            data = f.read()
            client_socket.sendall(data)
        print(f"文件 {send_filename} 发送完毕。")

        # 接收文件数据
        with open(receive_filename, 'wb') as f:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
        print(f"文件接收完毕，保存为：{receive_filename}")

