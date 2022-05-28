# -*- coding: utf-8 -*-
# Copyright (C) 2021 github.com/ItsChasa
#
# This source code has been released under the GNU Affero General Public
# License v3.0. A copy of this license is available at
# https://www.gnu.org/licenses/agpl-3.0.en.html

import requests, sys, time, os, ctypes
from colorama import Fore
white = Fore.WHITE
gray = Fore.LIGHTBLACK_EX
red = Fore.RED

from cfgload import Config

colours = {
    "light_red": Fore.LIGHTRED_EX,
    "dark_red": Fore.RED,
    "yellow": Fore.YELLOW,
    "dark_blue": Fore.BLUE,
    "light_blue": Fore.LIGHTBLUE_EX,
    "dark_cyan": Fore.CYAN,
    "light_cyan": Fore.LIGHTCYAN_EX,
    "green": Fore.LIGHTGREEN_EX,
    "purple": Fore.MAGENTA,
    "pink": Fore.LIGHTMAGENTA_EX,
    "gray": Fore.LIGHTBLACK_EX,
    "black": Fore.BLACK
}

class Setup():
    def welcome(self):
        print(f"""{self.maincol} ___               _                 
(  _ \            ( )                
| (_) )  _ _   ___| |/ ) _   _ _ _   
|  _ ( / _  )/ ___)   ( ( ) ( )  _ \ 
| (_) ) (_| | (___| |\ \| (_) | (_) )
(____/ \__ _)\____)_) (_)\___/|  __/ 
                              | |    
                              (_)    {self.white}
> Made with {self.maincol}<3{self.white} by {self.maincol}chasa{self.white}
> Github: {self.maincol}https://github.com/ItsChasa/Discord-Backup{self.white}
> Don't forget to {self.yellow}star{self.white} it!
> Version: {self.maincol}{self.version}""")
    
    def __init__(self, module, version):
        self.module = module
        self.version = version
        try: self.latest_ver = requests.get("https://api.github.com/repos/ItsChasa/Discord-Backup/releases/latest").json()['tag_name']
        except: self.latest_ver = version
        
        self.white = Fore.WHITE
        self.gray = Fore.LIGHTBLACK_EX
        self.red = Fore.RED
        self.green = Fore.LIGHTGREEN_EX
        self.yellow = Fore.YELLOW
        self.blue = Fore.LIGHTBLUE_EX

        try: cwd = sys.argv[2]
        except: pass
        else: os.chdir(cwd)
        
        try: self.cfg = Config()
        except:
            print("missing config file, redownload")
            time.sleep(3)
            os._exit(1)
        
        try: self.maincol = colours[self.cfg.colour]
        except: self.maincol = Fore.MAGENTA

        self.welcome()
        ctypes.windll.kernel32.SetConsoleTitleW(f"chasa.wtf | {self.module}")

        if self.latest_ver != version:
            print(f"\n{self.yellow}>{white} You are running an outdated version! Download the new version on GitHub: {self.latest_ver}")
    