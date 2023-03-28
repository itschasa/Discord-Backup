<div align="center">
    <h1>Discord Backup</h1>
    <p>☁️ Backup and Restore your Discord Account in minutes.</p>
    <img src="https://img.shields.io/github/license/ItsChasa/Discord-Backup?style=flat">
    <img src="https://img.shields.io/github/downloads/ItsChasa/Discord-Backup/total?style=flat">
    <img src="https://img.shields.io/github/stars/ItsChasa/Discord-Backup?style=flat">
    <img src="https://img.shields.io/github/forks/ItsChasa/Discord-Backup?style=flat">
    <img src="https://sonarcloud.io/api/project_badges/measure?project=itschasa_Discord-Backup&metric=ncloc"/>
    <br>
    <img src="https://github.com/ItsChasa/Discord-Backup/blob/main/img/backup-demo.gif">
    <br>
    <p><i>⭐ star the repo pls <3</i></p>
</div>



## Support + Community
[Discord Server](https://chasa.wtf/discord) | [Telegram Chat](https://chasa.wtf/telegram) | [Website](https://chasa.wtf/)


## Disclaimer 
The automation of Discord Accounts also known as self-bots is a violation of Discord Terms of Service & Community Guidelines and will result in your account(s) being terminated. Discretion is adviced. I will not be responsible for your actions. Read about Discord [Terms Of Service](https://discord.com/terms) and [Community Guidelines](https://discord.com/guidelines) here.


## **Features**:
### Automatic
These can be done by the program:
- Backup Servers
  - Save Server Invites
- Backup DM History
  - Save Users who have DMed you
- Backup Group Chats
  - Save Invites to Group Chats
- Backup Avatar, Banner and Bio
  - Saves 1 .txt and 2 .gif files
- Backup + Restore Server Folders
  - Saves the Order, Colour and Name of your Folders
- Backup + Restore Relationships
  - Save Friends, Blocked, Outgoing and Incoming Friends
- Auto-Backup on PC Startup
  - On Startup, automatically backup your Discord Account
- Colour Customisation
  - 12 different colours to choose from
### Manual
You will have to do this yourself:
- Restore Servers
  - You will have to join the Servers by clicking on an invite on Discord
- Restore Group Chats
  - You will have to join the Group Chats by clicking on an invite on Discord
- Restore Avatar, Banner and Bio
  - You will have to add these back through the User Profile menu


## Installation
### Using Binary EXE (Easier)
1. Download the zip for your Operating System from [Releases](https://github.com/itschasa/Discord-Backup/releases)
2. Unzip the contents into a folder
3. Run the exe

### Using Source
1. Install [Python 3.9.10](https://www.python.org/downloads/release/python-3910/) (should work with other versions)
2. Download source with the green `Code` button, then `Download ZIP`
3. Unzip the contents into a folder
4. Run in your command prompt:
```
pip install -r requirements.txt
```
5. Run main.py, either by double clicking or with command prompt (preferred way):
```
python main.py
```


## How to Use
1. Install using the instructions above and run the program.

### Backing Up
2. Select Option 1 to Backup a Discord Account.
3. You can scan for tokens (Discord Accounts) on your PC, or you can enter it manually.
  - If you aren't experienced with Discord, we recommend scanning your PC for tokens.
  - However, if you don't want to let the program do that or the account didn't show up when scanning, you can enter the token manually.
4. The program should now start to backup your account. This should take between 1m to 10m, depending on how many servers and group chats you are in.
5. Once the program has finished, you will see an overview of the backup where you can see if any guilds failed to be backed up. At this point, the .bkup file would be saved in the `backups` folder.
6. We also recommend you setup Auto-Backup, by selecting Option 3.

### Restoring
2. When you need to restore from a backup, select Option 2.
3. Select Option 1: Restore Everything.
4. You can now choose whether you want to restore your friends, outgoing, etc. Select `y` for yes or `n` for no on each one.
5. A new window will open, prompting you to select the .bkup file. Find it, and select it.
6. After you've checked the settings, select either `y` or `n`.
7. Now, you can choose whether to scan for tokens, or enter manually. Same instructions from `3.` in backing up apply here.
8. After you have entered your token, you need to enter a Bot Token. You can get one from the Discord Developer Portal.
- a. Go to https://discord.com/developers/applications
- b. Click `New Application` and enter a random name.
- c. On the sidebar, click `Bot`, then `Add Bot`, and `Yes, do it!`
- d. Click `Copy` (located next to `View Token`). The Bot Token is now in your clipboard!
9. The program will start to restore your account. Note: It's likely that this process will take longer then backing up, depending on how many relationships you had.
10. Like with the backing up, you will get an overview of what happened during the restoring process after it has finished.
11. After you have joined all the servers, you can go back into the program, and select Option 2: Restore Server Folders, to restore the server folders. Or, you can do this process manually.


## Notes / FAQ:
### Restoring Servers + Group Chats + Server Folders
Because of Discord's last resorts of using hCaptcha to stop people self-botting on Discord, I've decided its best to stop this program needing a captcha key.
- The program will create a server with all the old server invites in them, sorted into the folders from the old account.
- You simply just join them, when you need to.
- After you have joined all the servers, you can use the restore module to only restore folders.

### Group Chat Invites
Group Chat Invites are a bit scuffed on Discord.
- Server Invites will still be active if you leave the server.
- However, Group Chat Invites will not work **if you leave** the Group Chat.
- Meaning, if you leave the group chat after a backup, and before a term, then you won't be able to join that group chat back.

### Can I backup/restore an account which is already termed?
No. You can't, and never will be able to. Stop asking this.

### There's a feature I want to suggest.
Suggest it in the issues tab. I will probably add it.

### I keep getting an error, help!
Make an issue in the issue tab, or ask in the Community Servers.
