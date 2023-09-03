# Copyright (C) 2021 github.com/ItsChasa
#
# This source code has been released under the GNU Affero General Public
# License v3.0. A copy of this license is available at
# https://www.gnu.org/licenses/agpl-3.0.en.html

import base64
import time
import requests

import console
from main import request_client, colours
from client_info import build_headers

read_me_msg = """After you have joined all the servers, use option 2 on restore to get your server folders back!\n\nCoded with <3 by https://github.com/itschasa/discord-backup :)"""

class restore():
    def __init__(self, token, c: console.prnt, restore_server_folders, restore_data, bot_token, version) -> None:
        self.token = token
        self.c = c
        self.fatal_error = False
        self.before = time.time()
        self.bot_token = bot_token
        self.restore_data = restore_data

        if self.restore_data['version'] != version:
            self.c.warn(f"This Backup wasn't done on the same version of this software. (backup: {self.restore_data['version']}, current version:{version})")
            self.c.warn(f"This could lead to unexpected errors or side effects.")
            self.c.warn(f"It's recommended you change your software version to the same version as the backup was done on before continuing.")
            self.c.inp(f"Are you sure you want to continue? ({colours['main_colour']}y/n{colours['white']})", end=f"{colours['white']}")
            warning_continue = input()
            if warning_continue != "y":
                self.fatal_error = "Chose to stop restore"
                return

        token_check = request_client.get("https://discord.com/api/v9/users/@me", headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True))
        if token_check.status_code != 200:
            self.fatal_error = "Invalid User Token"
        else:
            self.user_me = token_check.json()

            bot_token_check = request_client.get("https://discord.com/api/v9/users/@me",
                headers={
                    'Authorization' : f'Bot {self.bot_token}',
                    'User-Agent': 'discord.py'
                }
            )
            if bot_token_check.status_code != 200:
                self.fatal_error = "Invalid Bot Token"
            else:
                print()

                self.user_data()
                fav_gifs_msg = self.favourited_gifs()
                self.servers()
                if restore_server_folders: self.folders()

                self.after = time.time()

                print()
                self.c.success(f"Restore Complete!")
                self.c.info(f"User Info + Avatar: {colours['main_colour']}Done")
                self.c.info(f"Favourited GIFs: {colours['main_colour']}{fav_gifs_msg}")
                self.c.info(f"Guild Folders: {colours['main_colour']}{'Done' if restore_server_folders else 'Disabled'}")
                self.c.info(f"Guilds: {colours['main_colour']}Done")
                self.c.info(f"Relationships: {colours['main_colour']}Done")
                self.c.info(f"Time Elapsed: {colours['main_colour']}{self._show_time(int(self.after - self.before))}")

    def _show_time(self, time):
        time = int(time)
        day = time // (24 * 3600)
        time = time % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time
        if day != 0: return "%d days %d hours" % (day, hour)
        elif day == 0 and hour != 0: return "%d hours %d minutes" % (hour, minutes)
        elif day == 0 and hour == 0 and minutes != 0: return "%d minutes %d seconds" % (minutes, seconds)
        else: return "%d seconds" % (seconds)

    def _snowflake(self):
        return str(int(bin(int((time.time() * 1000) - 1420070400000)).replace("0b", "") + "0000000000000000000000", 2))

    def _message(self, guild, channel, content) -> bool:
        headers = build_headers("post", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token,
                                    referer=f"https://discord.com/channels/{guild}/{channel}", timezone=True)
        payload = {
            "content": content,
            "nonce": self._snowflake(),
            "tts": False
        }
        while True:
            response = request_client.post(f"https://discord.com/api/v9/channels/{channel}/messages",
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                return True
            elif response.status_code == 429:
                self.c.warn("Rate Limited on Message Send")
                try: time.sleep(response.json()['retry_after'])
                except: time.sleep(3)
            else:
                print(response.json())
                return False

    @staticmethod
    def create_guild(token, payload, verbose=False):
        req = request_client.post("https://discord.com/api/v9/guilds",
            headers=build_headers("post", debugoptions=True, discordlocale=True, superprop=True, authorization=token, timezone=True, origin="https://discord.com"),
            json=payload
        )
        
        try: guild_id = req.json()['id']
        except:
            if verbose:
                print(f"Failed to create guild: {req.status_code}")
                print(req.text)
            return None, req
        else: return guild_id, req

    def servers(self):
        channels = [
            {
                "id": "0",
                "parent_id": None,
                "name": "read-me",
                "type": 0
            },
            {
                "id": "1",
                "parent_id": None,
                "name": "group-chats",
                "type": 0
            },
            {
                "id": "2",
                "parent_id": None,
                "name": "missing-guilds",
                "type": 0
            },
            {
                "id": "3",
                "parent_id": None,
                "name": "dm-history",
                "type": 0
            },
            {
                "id": "4",
                "parent_id": None,
                "name": "friends",
                "type": 0
            }
        ]
        for folder in self.restore_data['guild_folders']:
            channels.append(
                {
                    "id": str(self.restore_data['guild_folders'].index(folder) + 5),
                    "parent_id": None,
                    "name": f"folder-{self.restore_data['guild_folders'].index(folder)}",
                    "type": 0
                }
            )
        
        try:
            imgdata = base64.b64encode(requests.get("https://i.imgur.com/b6B3Fbw.jpg").content).decode()
            if len(imgdata) < 500:
                raise Exception
            else:
                imgdata = "data:image/jpeg;base64," + imgdata
        except:
            imgdata = None

        payload = {
            "name": "Backup Server",
            "icon": imgdata,
            "channels": channels,
            "system_channel_id": "0",
            "guild_template_code": "2TffvPucqHkN",
        }

        guild_id, req = self.create_guild(self.token, payload)
        
        if not guild_id:
            self.c.fail(f"Failed to create guild: {req.status_code}")
            self.c.fail(req.text)
            self.fatal_error = "Failed to create guild"
            return
        
        missing_guilds_chn_id = None
        group_chat_id = None
        missing_guilds = [""]

        self.c.success("Created Guild")

        guild_channels = request_client.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels",
            headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True)
        ).json()

        for chn in guild_channels:
            if chn['name'] == "read-me":
                self._message(guild_id, chn['id'], read_me_msg)
            elif chn['name'] == "missing-guilds":
                missing_guilds_chn_id = chn['id']
            elif chn['name'] == "group-chats":
                group_chat_id = chn['id']
            elif chn['name'] == "dm-history":
                dm_history_id = chn['id']
            elif chn['name'] == "friends":
                friend_chnl_id = chn['id']
            else:
                folder_id = int(chn['name'].replace("folder-", ""))
                cnt = [f"**Folder Name:** {self.restore_data['guild_folders'][folder_id]['name']}\n\n"]

                for gld_id in self.restore_data['guild_folders'][folder_id]['guild_ids']:
                    invite_data = False
                    for inv in self.restore_data['guilds']:
                        if str(inv['id']) == str(gld_id):
                            invite_data = inv
                    if invite_data is False:
                        self.c.warn(f"Couldn't find invite for guild: {colours['main_colour']}{gld_id}")
                        missing_guilds_dat = f"ID: `{gld_id}` | Server was in Server Folders, but not in invites.\n\n"
                        if len(missing_guilds[-1]) + len(missing_guilds_dat) > 2000:
                            missing_guilds.append(missing_guilds_dat)
                        else:
                            missing_guilds[-1] += missing_guilds_dat
                    else:
                        if invite_data['invite-code'] != "Unable to create.":
                            dat = f"{invite_data['name']} (`{invite_data['id']}`)\nhttps://discord.gg/{invite_data['invite-code']}\n\n"
                            if len(cnt[-1]) + len(dat) > 2000:
                                cnt.append(dat)
                            else:
                                cnt[-1] += dat
                            self.c.success(f"Found data for guild: {colours['main_colour']}{invite_data['name']}")
                        else:
                            self.c.warn(f"Invite wasn't created for: {colours['main_colour']}{invite_data['name']}")
                            missing_guilds_dat = f"Name: `{invite_data['name']}` | ID: `{gld_id}` | Invite wasn't made on backup (missing perms). \n\n"
                            if len(missing_guilds[-1]) + len(missing_guilds_dat) > 2000:
                                missing_guilds.append(missing_guilds_dat)
                            else:
                                missing_guilds[-1] += missing_guilds_dat

                for msg in cnt:
                    self.c.warn("Sleeping 1 second")
                    time.sleep(1)
                    if self._message(guild_id, chn['id'], msg):
                        self.c.success(f"Sent message in Channel: {colours['main_colour']}#{chn['name']}")
                    else:
                        self.c.fail(f"Failed to send message in Channel: {colours['main_colour']}#{chn['name']}")
                

        for msg in missing_guilds:
            self.c.warn("Sleeping 1 second")
            time.sleep(1)
            if self._message(guild_id, missing_guilds_chn_id, msg):
                self.c.success(f"Sent message in Channel: {colours['main_colour']}#missing-guilds")
            else:
                self.c.fail(f"Failed to send message in Channel: {colours['main_colour']}#missing-guilds")

        
        group_chats = ["**Invites for Group Chats only last 7 days, so if your backup is old, then these might all be invalid.**\nAnother Note: Your old account must still be in these group chats. Being termed is ok. However, if your old account was kicked/left the group chats, then these invites will be invalid.\n\n"]
        for gc in self.restore_data['group-chats']:
            dat = f"**{gc['name']}**\nhttps://discord.gg/{gc['invite-code']}\n\n"
            if len(group_chats[-1]) + len(dat) > 2000:
                group_chats.append(dat)
            else:
                group_chats[-1] += dat
        
        for msg in group_chats:
            self.c.warn("Sleeping 1 second")
            time.sleep(1)
            if self._message(guild_id, group_chat_id, msg):
                self.c.success(f"Sent message in Channel: {colours['main_colour']}#group-chats")
            else:
                self.c.fail(f"Failed to send message in Channel: {colours['main_colour']}#group-chats")

        dm_messages = ["**DM History**\nFormat: `user#tag | user ping | last_dm`\n(sorted most recent at top)\n\n"]
        for dm in self.restore_data['dm-history']:
            tmstmp = f"<t:{dm['timestamp']}>" if dm['timestamp'] != 0 else "Never DMed"
            dat = f"{dm['user']} | <@{dm['user_id']}> | {tmstmp}\n"
            if len(dm_messages[-1]) + len(dat) > 2000:
                dm_messages.append(dat)
            else:
                dm_messages[-1] += dat

        for msg in dm_messages:
            self.c.warn("Sleeping 1 second")
            time.sleep(1)
            if self._message(guild_id, dm_history_id, msg):
                self.c.success(f"Sent message in Channel: {colours['main_colour']}#dm-history")
            else:
                self.c.fail(f"Failed to send message in Channel: {colours['main_colour']}#dm-history")
        
        friend_msgs = ["**Friends/Relationships**\n\n"]
        
        if len(self.restore_data['friends']) != 0:
            dat = f"\nFriends\n"
            if len(friend_msgs[-1]) + len(dat) > 2000:
                friend_msgs.append(dat)
            else:
                friend_msgs[-1] += dat
            
            for dm in self.restore_data['friends']:
                dat = f"<@{dm}> | {self._get_user_info(dm)}\n"
                if len(friend_msgs[-1]) + len(dat) > 2000:
                    friend_msgs.append(dat)
                else:
                    friend_msgs[-1] += dat
        
        if len(self.restore_data['incoming']) != 0:
            dat = f"\nIncoming\n"
            if len(friend_msgs[-1]) + len(dat) > 2000:
                friend_msgs.append(dat)
            else:
                friend_msgs[-1] += dat
            
            for dm in self.restore_data['incoming']:
                dat = f"<@{dm}> | {self._get_user_info(dm)}\n"
                if len(friend_msgs[-1]) + len(dat) > 2000:
                    friend_msgs.append(dat)
                else:
                    friend_msgs[-1] += dat

        if len(self.restore_data['outgoing']) != 0:
            dat = f"\nOutgoing\n"
            if len(friend_msgs[-1]) + len(dat) > 2000:
                friend_msgs.append(dat)
            else:
                friend_msgs[-1] += dat
            
            for dm in self.restore_data['outgoing']:
                dat = f"<@{dm}> | {self._get_user_info(dm)}\n"
                if len(friend_msgs[-1]) + len(dat) > 2000:
                    friend_msgs.append(dat)
                else:
                    friend_msgs[-1] += dat

        if len(self.restore_data['blocked']) != 0:
            dat = f"\nBlocked\n"
            if len(friend_msgs[-1]) + len(dat) > 2000:
                friend_msgs.append(dat)
            else:
                friend_msgs[-1] += dat
            
            for dm in self.restore_data['blocked']:
                dat = f"<@{dm}> | {self._get_user_info(dm)}\n"
                if len(friend_msgs[-1]) + len(dat) > 2000:
                    friend_msgs.append(dat)
                else:
                    friend_msgs[-1] += dat

        for msg in friend_msgs:
            self.c.warn("Sleeping 1 second")
            time.sleep(1)
            if self._message(guild_id, friend_chnl_id, msg):
                self.c.success(f"Sent message in Channel: {colours['main_colour']}#friends")
            else:
                self.c.fail(f"Failed to send message in Channel: {colours['main_colour']}#friends")        
        

    def user_data(self):
        time_now = int(time.time())
        f = open(f"pfp-{time_now}.gif", "wb")
        f.write(base64.b64decode(self.restore_data['avatar-bytes']))
        f.close()
        self.c.success(f"Saved avatar: {colours['main_colour']}pfp-{time_now}.png")
        
        f = open(f"bio-{time_now}.txt", "w", encoding="utf-8")
        f.write(self.restore_data['bio'])
        f.close()
        self.c.success(f"Saved bio: {colours['main_colour']}bio-{time_now}.txt")

        if self.restore_data['banner-bytes'] != "":
            f = open(f"banner-{time_now}.gif", "wb")
            f.write(base64.b64decode(self.restore_data['banner-bytes']))
            f.close()
            self.c.success(f"Saved banner: {colours['main_colour']}banner-{time_now}.gif")
    
    def _get_user_info(self, userid):
        while True:
            req = request_client.get(f'https://discord.com/api/v9/users/{userid}',
                # seems like Cloudflare blocks requests that:
                # 1) have a bot token
                # 2) contain a browser user-agent
                # probably to make sure bot devs identify what library they are using (for analytical purposes?)
                
                headers={
                    'Authorization' : f'Bot {self.bot_token}',
                    'User-Agent': 'discord.py'
                }
            )
            if "You are being rate limited." in req.text:
                self.c.warn(f"Rate Limited: {colours['main_colour']}{req.json()['retry_after']} seconds{colours['white']}.")
                time.sleep(req.json()["retry_after"])
            else:
                if req.status_code != 200:
                    self.c.fail(f"Couldn't fetch username: {colours['main_colour']}{userid}{colours['white']} ({req.json()['message']})")
                    return 'Error'
                else:
                    self.c.success(f"Fetched username: {colours['main_colour']}{userid}{colours['white']}.")
                    return f"{req.json()['username']}#{req.json()['discriminator']}"
        
    
    def folders(self):
        while True:
            user_guilds_req = request_client.get(f"https://discord.com/api/v9/users/@me/guilds",
                headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True)
            )
            if "You are being rate limited." in user_guilds_req.text:
                self.c.warn(f"Rate Limited: {colours['main_colour']}{user_guilds_req.json()['retry_after']} seconds{colours['white']}.")
                time.sleep(user_guilds_req.json()["retry_after"])
            else:
                break
        
        guild_ids = []
        for gld in user_guilds_req.json():
            guild_ids.append(gld['id'])

        data_to_send = []
        for folder in self.restore_data["guild_folders"]:
            tmp = folder
            for guild in folder["guild_ids"]:
                if str(guild) not in guild_ids:
                    tmp["guild_ids"].remove(str(guild))
            data_to_send.append(tmp)

        while True:
            r = request_client.patch(f"https://discord.com/api/v9/users/@me/settings",
                headers = build_headers("patch", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True),
                json = {"guild_folders": data_to_send}
            )
            if "You are being rate limited." in r.text:
                self.c.warn(f"Rate Limited: {colours['main_colour']}{r.json()['retry_after']} seconds{colours['white']}.")
                time.sleep(r.json()["retry_after"])
            else:
                break

        if r.status_code == 200:
            self.c.success(f"Restored Guild Folders")
        else:
            self.c.fail(f"Couldn't Restore Guild Folders: {colours['main_colour']}{r.status_code}")
    
    def favourited_gifs(self):
        if self.restore_data.get('settings') == None:
            self.c.warn(f"Couldn't Find Favourite GIFs on Backup")
            return "Wasn't on Backup"
        else:
            r = request_client.patch(f"https://discord.com/api/v9/users/@me/settings-proto/2",
                headers = build_headers("patch", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True),
                json = {"settings": self.restore_data['settings']}
            )
            if r.status_code == 200:
                self.c.success(f"Restored Favourited GIFs")
                return "Done"
            else:
                self.c.fail(f"Couldn't Restore Favourited GIFs: {r.status_code}")
                return "Failed"
            
