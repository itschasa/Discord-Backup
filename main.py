# -*- coding: utf-8 -*-
# Copyright (C) 2021 github.com/ItsChasa
#
# This source code has been released under the GNU Affero General Public
# License v3.0. A copy of this license is available at
# https://www.gnu.org/licenses/agpl-3.0.en.html

app_version = "v1.2.9"

import time
import sys
import base64
import os
import json
import ctypes
from pathlib import Path
from easygui import fileopenbox
from colorama import Fore

from client_info import request_client, discord_build, discord_build_failback

# change cwd (for auto-backup)
try: cwd = sys.argv[2]
except: pass
else: os.chdir(cwd)

import cfgload
try: config = cfgload.Config()
except:
    print("Config File was not found (config.yml), make sure it exists.")
    time.sleep(3)
    os._exit(1)

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
    "black": Fore.BLACK,
    "white": Fore.WHITE,
}
try: colours['main_colour'] = colours[config.colour]
except: colours['main_colour'] = Fore.MAGENTA

if __name__ == '__main__':
    import console
    import backup
    import restore
    c = console.prnt()
    
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        github_data = request_client.get("https://api.github.com/repos/ItsChasa/Discord-Backup/releases/latest").json()
        app_latest_ver = github_data['tag_name']
        app_latest_ver_link = github_data['html_url']
    except:
        app_latest_ver = app_version
        app_latest_ver_link = "null"
    
    print(f"""{colours['main_colour']}
 ___               _                 
(  _ \            ( )                
| (_) )  _ _   ___| |/ ) _   _ _ _   
|  _ ( / _  )/ ___)   ( ( ) ( )  _ \ 
| (_) ) (_| | (___| |\ \| (_) | (_) )
(____/ \__ _)\____)_) (_)\___/|  __/ 
                              | |    
                              (_)    {colours['white']}
> Made with {colours['main_colour']}<3{colours['white']} by {colours['main_colour']}chasa{colours['white']}
> Github: {colours['main_colour']}https://github.com/itschasa/Discord-Backup{colours['white']}
> Don't forget to {colours['yellow']}star{colours['white']} it!
> Version: {colours['main_colour']}{app_version}{colours['white']}
> Discord Build: {colours['main_colour']}{colours['main_colour']}{discord_build}{colours['white']}{'' if not discord_build_failback else ' (failback)'}""")
        
    try: ctypes.windll.kernel32.SetConsoleTitleW(f"github.com/itschasa/Discord-Backup")
    except: pass

    if app_latest_ver != app_version:
        print()
        c.warn(f"You are running an outdated version! Download the new version on GitHub: {app_latest_ver}")
        c.warn(app_latest_ver_link)

    try: cwd = sys.argv[2]
    except: account_id = None
    else:
        os.chdir(cwd)
        account_id = sys.argv[1]

    while True:
        choice = 0
        if account_id == None:
            print(f""" 
{colours['white']}> Main Menu
{colours['white']}1: {colours['main_colour']}Backup
{colours['white']}2: {colours['main_colour']}Restore
{colours['white']}3: {colours['main_colour']}Add to Startup
{colours['white']}4: {colours['main_colour']}Help

{colours['light_blue']}>{colours['white']} Choice ({colours['main_colour']}int{colours['white']}) """, end="")
            choice = input()
            try: choice = int(choice)
            except: choice = ""
        else:
            choice = 1
        print()
        if choice == 1:
            token_info = False
            if account_id != None:
                c.info(f"Launching Auto-Backup on ID: {colours['main_colour']}{account_id}")
                account_id_b64 = base64.b64encode(str(account_id).encode()).decode().replace('=', '')
                import fetch_tokens
                c.info(f"Scanning for tokens...")
                tokens = fetch_tokens.fetch()
                for tkn in tokens:
                    if str(tkn[0]).startswith(account_id_b64):
                        token_info = tkn
                        break
                if token_info is False:
                    c.fail("Could not find valid token with the provided ID.")
                    c.fail("Exiting in 5 seconds...")
                    time.sleep(5)
                    os._exit(1)
                else:
                    c.success(f"Found token with matching ID: {colours['main_colour']}{token_info[1]}")
                    c.info("Starting Backup...")
            else:
                c.inp(f"Scan for tokens? ({colours['main_colour']}y/n{colours['white']}) ", end=colours['white'])
                if input().lower() == "y":
                    import fetch_tokens
                    c.info(f"Scanning for tokens...")
                    tokens = fetch_tokens.fetch()
                    if len(tokens) != 0:
                        print()
                        while True:
                            c.info(f"Select which token you want to be auto-backed up:")
                            for tkn in tokens:
                                print(f"{colours['white']}{tokens.index(tkn)}: {colours['main_colour']}{tkn[1]}{colours['white']} from {colours['main_colour']}{tkn[3]}")
                            print()
                            c.inp(f"Choice {colours['main_colour']}(int) """, end=colours['white'])
                            try: tknchoice = int(input())
                            except ValueError: c.fail(f"Invalid Choice")
                            else:
                                try:
                                    token_selected = tokens[tknchoice]
                                except:
                                    c.fail(f"Invalid Choice")
                                else:
                                    break
                        c.success(f"Selected {colours['main_colour']}{token_selected[1]}")
                        token_info = token_selected
                    else:
                        c.fail(f"No tokens were found on your system.")
                else:
                    c.inp("Token: ", end="")
                    token_info = [input(), ""]
                    
            
            if token_info != False:
                bkup = backup.backup(token_info[0], c, app_version)
                if bkup.fatal_error != False:
                    c.fail(bkup.fatal_error)
            if len(sys.argv) > 2:
                print()
                c.warn("Closing in 5 seconds...")
                time.sleep(5)
                os._exit(0)


        elif choice == 2:
            c.info(f"1: {colours['main_colour']}Restore Everything")
            c.info(f"2: {colours['main_colour']}Restore Server Folders")
            c.info(f"See help for more info.")
            print()
            c.inp(f"Choice ({colours['main_colour']}int{colours['white']}) ", end="")
            try:
                choice = int(input())
                if choice not in [1,2]: raise Exception
            except:
                c.fail(f"Invalid Choice")
            else:
                restore_server_folders = False
                start_restore = False
                if choice == 1:
                    try:
                        c.inp(f"Select backup file in new window.")
                        backupfile = fileopenbox(title="Load .bkup File", default="*.bkup")
                        backup_data = json.loads(open(backupfile, "r", encoding="utf-8").read())
                    except Exception as e:
                        c.fail("Encountered Error whilst loading backup file.")
                        c.fail(f"{e}")
                    else:
                        c.success(f"Loaded backup data.")
                        start_restore = True
                else:
                    restore_server_folders = True
                    try:
                        c.inp(f"Select backup file in new window.")
                        backupfile = fileopenbox(title="Load .bkup File", default="*.bkup")
                        backup_data = json.loads(open(backupfile, "r", encoding="utf-8").read())
                    except Exception as e:
                        c.fail("Encountered Error whilst loading backup file.")
                        c.fail(f"{e}")
                    else:
                        c.success(f"Loaded server folders.")
                        start_restore = True

                if start_restore is True:
                    c.inp(f"Scan for tokens? ({colours['main_colour']}y/n{colours['white']}) ({colours['main_colour']}account to restore on to{colours['white']}) ", end=colours['white'])
                    if input().lower() == "y":
                        import fetch_tokens
                        c.info(f"Scanning for tokens...")
                        tokens = fetch_tokens.fetch()
                        if len(tokens) != 0:
                            while True:
                                print()
                                c.info(f"Select which token you want to be auto-backed up:")
                                for tkn in tokens:
                                    print(f"{colours['white']}{tokens.index(tkn)}: {colours['main_colour']}{tkn[1]}{colours['white']} from {colours['main_colour']}{tkn[3]}")
                                print()
                                c.inp(f"Choice {colours['main_colour']}(int) """, end=colours['white'])
                                try: tknchoice = int(input())
                                except ValueError: c.fail(f"Invalid Choice")
                                else:
                                    try:
                                        token_selected = tokens[tknchoice]
                                    except:
                                        c.fail(f"Invalid Choice")
                                    else:
                                        break
                            c.success(f"Selected {colours['main_colour']}{token_selected[1]}")
                            token_info = token_selected
                        else:
                            c.fail(f"No tokens were found on your system.")
                    else:
                        c.inp("Token: ", end="")
                        token_info = [input(), ""]
                    
                    c.info("A Bot Token is required to fetch Usernames from IDs (used for friends/blocked). You can create one in the Discord Developer Portal.")
                    c.inp("Bot Token: ", end="")
                    bot_token = input()
                    
                    rstr = restore.restore(token_info[0], c, restore_server_folders, backup_data, bot_token, app_version)
                    if rstr.fatal_error != False:
                        c.fail(rstr.fatal_error)


        
        elif choice == 3:
            c.inp(f"By adding to startup, you agree that this program is allowed to search for tokens on your PC.")
            c.inp(f"Your Account Token is only sent to discord's servers. ({colours['main_colour']}y/n{colours['white']}) ", end=f"{colours['white']}")
            if input().lower() == "y":
                import fetch_tokens
                c.info(f"Scanning for tokens...")
                tokens = fetch_tokens.fetch()
                if len(tokens) != 0:
                    while True:
                        print()
                        c.info(f"Select which token you want to be auto-backed up:")
                        for tkn in tokens:
                            print(f"{colours['white']}{tokens.index(tkn)}: {colours['main_colour']}{tkn[1]}{colours['white']} from {colours['main_colour']}{tkn[3]}")
                        print()
                        c.inp(f"Choice {colours['main_colour']}(int) """, end=colours['white'])
                        try: tknchoice = int(input())
                        except ValueError: c.fail(f"Invalid Choice")
                        else:
                            try:
                                token_selected = tokens[tknchoice]
                            except:
                                c.fail(f"Invalid Choice")
                            else:
                                break

                    c.success(f"Selected {colours['main_colour']}{token_selected[1]}")
                    
                    try:
                        if getattr(sys, 'frozen', False): # if pyinstaller
                            tmp_path = ""
                            dirs_list = sys.executable.split("\\")
                            for dir in dirs_list[0:-1]:
                                tmp_path += dir + "\\"
                            application_path = tmp_path[0:-1]
                            application_name = dirs_list[-1]
                            prefix_for_command = ""
                        else:
                            application_path = os.path.dirname(os.path.abspath(__file__))
                            application_name = Path(__file__).name
                            prefix_for_command = "cmd.exe /C python "

                    except:
                        c.fail(f"Failed to find Executable.")
                    else:
                        roaming = os.getenv('APPDATA')
                        f = open(f"{roaming}\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\backupStartup.vbs", "w")
                        f.write(f'Set oShell = CreateObject ("WScript.Shell")')
                        f.write("\n")
                        f.write(f'oShell.run "{prefix_for_command}""{application_path}\{application_name}"" {token_selected[2]} ""{application_path}"""')
                        f.close()
                        
                        c.success(f"Added to startup! ({colours['main_colour']}{roaming}\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\backupStartup.vbs{colours['white']})")
                else:
                    c.fail(f"No tokens were found on your system.")
        
        elif choice == 4:
            c.info('Go to: https://github.com/itschasa/Discord-Backup#how-to-use')
            c.info('For additional help, join the Discord Server: https://discord.gg/MUP5TSEPc4')
            c.info("If it's invalid, go to https://chasa.wtf and click the Discord icon.")
        
        elif choice == 999:
            c.info("Test Guild Creation (TLS Client)")
            c.inp("Token: ", end="")
            token = input()
            restore.restore.create_guild(
                token,
                {
                    "name": "Test Server",
                    "icon": None,
                    "channels": [],
                    "system_channel_id": "0",
                    "guild_template_code": "2TffvPucqHkN",
                },
                verbose=True
            )

        else:
            c.fail(f"Invalid Choice")
        
        time.sleep(0.5)

