import pygame as pg
from GameControl.game import Game
from GameControl.EventManager import show_menu, EtatJeu, open_network_setting
from pygame.locals import *
# from GameControl.inputManager import *
from GameControl.setting import Setting
# from GameControl.gameControl import GameControl
import sys
import os
import subprocess  # Add this import
from socket import gethostname, gethostbyname # Add
import atexit

flags = HWSURFACE | DOUBLEBUF

def main():
    etat = EtatJeu.getEtatJeuInstance()
    pg.init()
    pg.mixer.init()
    # screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    screen = pg.display.set_mode((1920, 1080), HWSURFACE | DOUBLEBUF)
    # screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    clock = pg.time.Clock()
    # setting = Setting.getSettings()
    # implement menus

    # implement game

    print(etat.running)
    emetteur_process = None  # Initialize process variable
    recepteur_process = None  # Initialize process variable

    while etat.running:

        if etat.open_menu:
            show_menu(screen, clock)
        elif etat.playing:
            # Start the C programs in the background
            if emetteur_process is None and recepteur_process is None:
                emetteur_process = subprocess.Popen(["./emetteur"])
                recepteur_process = subprocess.Popen(["./recepteur"])

            game = Game.getInstance(screen, clock)
            if etat.game_instance == 0:
                game.createNewGame()
            else:
                game.loadGame(etat.game_instance)
            game.run()
        elif etat.online_menu:
            open_network_setting(screen, clock)

    # Cleanup: Ensure subprocesses are terminated when the main program exits
    

def cleanup_processes():
    if main.emetteur_process is not None:
        main.emetteur_process.terminate()
        main.emetteur_process.wait()
    if main.recepteur_process is not None:
        main.recepteur_process.terminate()
        main.recepteur_process.wait()

def cleanup_files():
    # 清空文件内容
    files_to_clear = ["GameControl/testdata.json", "GameControl/testdata1.json"]
    for file in files_to_clear:
        try:
            with open(file, 'w') as f:
                pass  # 打开文件并立即关闭，以清空文件内容
            print(f"文件 '{file}' 内容已清空")
        except OSError as e:
            print(f"清空文件 '{file}' 内容时出错: {e}")

# 注册清理函数
atexit.register(cleanup_files)
atexit.register(cleanup_processes)
    
    # files_to_delete = ["GameControl/testdata.json", "GameControl/testdata1.json"]

    # # 遍历文件列表，逐个删除
    # for file in files_to_delete:
    #     try:
    #         os.remove(file)
    #         print(f"文件 '{file}' 删除成功")
    #     except OSError as e:
    #         print(f"删除文件 '{file}' 时出错: {e}")
        

            

if __name__ == "__main__":
    main()

