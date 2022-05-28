# Copyright (C) 2021 github.com/ItsChasa
#
# This source code has been released under the GNU Affero General Public
# License v3.0. A copy of this license is available at
# https://www.gnu.org/licenses/agpl-3.0.en.html

import requests, base64, time, random

import console

read_me_msg = """Due to the current situation with captchas, I've decided that it would be easier to put all the invites into a server for you to join.\n\nCaptcha solvers right now are quite "on and off", meaning they sometimes work, and sometimes they don't.\n\nAlso note, if you just made this account, don't join all the servers at once. There's a good chance you will get locked.\n\nAfter you have joined all the servers, you can restore your original folders automatically, by using option 2 on the restore module.\nHowever, you can do this manually if you prefer.\n\n\n*Brought to you with <3 by github.com/itschasa/discord-backup :)*"""

class restore():
    def __init__(self, token, c: console.prnt, restore_servers, restore_friends, restore_blocked, restore_outgoing, restore_incoming, restore_server_folders, restore_data) -> None:
        self.restore_data = restore_data
        self.token = token
        self.c = c
        self.fatal_error = False
        self.before = time.time()

        self.restore_friends = restore_friends
        self.restore_blocked = restore_blocked
        self.restore_outgoing = restore_outgoing
        self.restore_incoming = restore_incoming
        
        token_check = requests.get("https://discord.com/api/v9/users/@me", headers=self._headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=True))
        if token_check.status_code != 200:
            self.fatal_error = "Invalid Token"
        else:
            self.user_me = token_check.json()
            
            print()

            self.user_data()
            if restore_servers: self.servers()
            if restore_server_folders: self.folders()
            self.relationships()

            self.after = time.time()

            print()
            self.c.success(f"Restore Complete!")
            self.c.info(f"User Info + Avatar: {self.c.clnt.maincol}Done")
            self.c.info(f"Guild Folders: {self.c.clnt.maincol}{'Done' if restore_server_folders else 'Disabled'}")
            self.c.info(f"Guilds: {self.c.clnt.maincol}{'Done' if restore_servers else 'Disabled'}")
            self.c.info(f"Relationships:")
            self.c.info(f"Friends: {self.c.clnt.maincol}{self.friends_added}/{len(self.friends)}", indent=2)
            self.c.info(f"Blocked: {self.c.clnt.maincol}{self.blocked_added}/{len(self.to_block)}", indent=2)
            self.c.info(f"Incoming: {self.c.clnt.maincol}{self.incoming_added}/{len(self.incoming)}", indent=2)
            self.c.info(f"Outgoing: {self.c.clnt.maincol}{self.outgoing_added}/{len(self.outgoing)}", indent=2)
            self.c.info(f"Time Elapsed: {self.c.clnt.maincol}{self._show_time(int(self.after - self.before))}")

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
    
    def _headers(self, method, superprop=False, debugoptions=False, discordlocale=False, authorization=False, origin=False, referer="https://discord.com/channels/@me", context=False):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": "locale=en-GB",
            "Referer": referer,
            "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }

        if referer == False:
            del headers["Referer"]
        
        if method != "get":
            headers["Content-Type"] = "application/json"
            headers["Origin"] = "https://discord.com"

        if authorization == True:
            headers["Authorization"] = self.token
        if origin != False:
            headers["Origin"] = origin
        if debugoptions == True:
            headers["X-Debug-Options"] = "bugReporterEnabled"
        if discordlocale == True:
            headers["X-Discord-Locale"] = "en-US"
        if superprop == True:
            headers["X-Super-Properties"] = "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMC4wLjQ4OTYuMTI3IFNhZmFyaS81MzcuMzYiLCJicm93c2VyX3ZlcnNpb24iOiIxMDAuMC40ODk2LjEyNyIsIm9zX3ZlcnNpb24iOiIxMCIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoxMjY0NjIsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
        if context != False:
            headers["X-Context-Properties"] = context
        
        keyssorted = sorted(headers.keys(), key=lambda x:x.lower())
        newheaders={}
        for key in keyssorted:
            newheaders[key] = headers[key]

        return headers

    def _snowflake(self):
        return str(int(bin(int((time.time() * 1000) - 1420070400000)).replace("0b", "") + "0000000000000000000000", 2))

    def _message(self, guild, channel, content) -> bool:
        headers = self._headers("post", debugoptions=True, discordlocale=True, superprop=True, authorization=True,
                                    referer=f"https://discord.com/channels/{guild}/{channel}")
        payload = {
            "content": content,
            "nonce": self._snowflake(),
            "tts": False
        }
        while True:
            response = requests.post(f"https://discord.com/api/v9/channels/{channel}/messages",
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
            }
        ]
        for folder in self.restore_data['guild_folders']:
            channels.append(
                {
                    "id": str(self.restore_data['guild_folders'].index(folder) + 3),
                    "parent_id": None,
                    "name": f"folder-{self.restore_data['guild_folders'].index(folder)}",
                    "type": 0
                }
            )
        
        imgdata = base64.b64encode(requests.get("https://i.imgur.com/b6B3Fbw.jpg").content).decode()
        payload = {
            "channels": channels,
            "guild_template_code": "FbwUwRp4j8Es",
            "icon": f"data:image/jpeg;base64,{imgdata}",
            "name": "Backup Server",
            "system_channel_id": "0",
        }

        req = requests.post("https://discord.com/api/v9/guilds",
            headers=self._headers("post", debugoptions=True, discordlocale=True, superprop=True, authorization=True),
            json=payload
        )

        guild_id = req.json()['id']
        missing_guilds_chn_id = None
        group_chat_id = None
        missing_guilds = [""]

        self.c.success("Created Guild")

        guild_channels = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels",
            headers=self._headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=True)
        ).json()

        for chn in guild_channels:
            if chn['name'] == "read-me":
                self._message(guild_id, chn['id'], read_me_msg)
            elif chn['name'] == "missing-guilds":
                missing_guilds_chn_id = chn['id']
            elif chn['name'] == "group-chats":
                group_chat_id = chn['id']
            else:
                folder_id = int(chn['name'].replace("folder-", ""))
                cnt = [f"----\n**Folder Name: {self.restore_data['guild_folders'][folder_id]['name']}**\n----\n\n"]

                for gld_id in self.restore_data['guild_folders'][folder_id]['guild_ids']:
                    invite_data = False
                    for inv in self.restore_data['guilds']:
                        if str(inv['id']) == str(gld_id):
                            invite_data = inv
                    if invite_data == False:
                        self.c.warn(f"Couldn't find invite for guild: {self.c.clnt.maincol}{gld_id}")
                        missing_guilds_dat = f"Server was in Server Folders, but not in invites. ID: {gld_id}\n\n"
                        if len(missing_guilds[-1]) + len(missing_guilds_dat) > 2000:
                            missing_guilds.append(missing_guilds_dat)
                        else:
                            missing_guilds[-1] += missing_guilds_dat
                    else:
                        if invite_data['invite-code'] != "Unable to create.":
                            dat = f"**{invite_data['name']}**\nhttps://discord.gg/{invite_data['invite-code']}\n\n"
                            if len(cnt[-1]) + len(dat) > 2000:
                                cnt.append(dat)
                            else:
                                cnt[-1] += dat
                            self.c.success(f"Found data for guild: {self.c.clnt.maincol}{invite_data['name']}")
                        else:
                            self.c.warn(f"Invite wasn't created for: {self.c.clnt.maincol}{invite_data['name']}")
                            missing_guilds_dat = f"Invite wasn't made on backup (missing perms). ID: {gld_id} | Name: {invite_data['name']}\n\n"
                            if len(missing_guilds[-1]) + len(missing_guilds_dat) > 2000:
                                missing_guilds.append(missing_guilds_dat)
                            else:
                                missing_guilds[-1] += missing_guilds_dat

                for msg in cnt:
                    if self._message(guild_id, chn['id'], msg):
                        self.c.success(f"Sent message in Channel: {self.c.clnt.maincol}#{chn['name']}")
                    else:
                        self.c.fail(f"Failed to send message in Channel: {self.c.clnt.maincol}#{chn['name']}")
        
        for msg in missing_guilds:
            if self._message(guild_id, missing_guilds_chn_id, msg):
                self.c.success(f"Sent message in Channel: {self.c.clnt.maincol}#missing-guilds")
            else:
                self.c.fail(f"Failed to send message in Channel: {self.c.clnt.maincol}#missing-guilds")
        
        
        group_chats = ["**Invites for Group Chats only last 7 days, so if your backup is old, then these might all be invalid.**\nAnother Note: Your old account must still be in these group chats. Being termed is ok. However, if your old account was kicked/left the group chats, then these invites will be invalid.\n\n"]
        for gc in self.restore_data['group-chats']:
            dat = f"**{gc['name']}**\nhttps://discord.gg/{gc['invite-code']}\n\n"
            if len(group_chats[-1]) + len(dat) > 2000:
                group_chats.append(dat)
            else:
                group_chats[-1] += dat
        
        for msg in group_chats:
            if self._message(guild_id, group_chat_id, msg):
                self.c.success(f"Sent message in Channel: {self.c.clnt.maincol}#group-chats")
            else:
                self.c.fail(f"Failed to send message in Channel: {self.c.clnt.maincol}#group-chats")


    def relationships(self):
        to_add = []
        self.to_block = []
        self.friends = []
        self.friends_added = 0
        self.outgoing = []
        self.outgoing_added = 0
        self.incoming = []
        self.incoming_added = 0
        self.blocked_added = 0

        if self.restore_friends:
            to_add.extend(self.restore_data['friends'])
            self.friends = self.restore_data['friends']
        if self.restore_incoming:
            to_add.extend(self.restore_data['incoming'])
            self.incoming = self.restore_data['incoming']
        if self.restore_outgoing:
            to_add.extend(self.restore_data['outgoing'])
            self.outgoing = self.restore_data['outgoing']
        if self.restore_blocked:
            self.to_block.extend(self.restore_data['blocked'])

        for user in to_add:
            while True:
                r = requests.put(f"https://discord.com/api/v9/users/@me/relationships/{user}",
                    headers = self._headers("put", debugoptions=True, discordlocale=True, superprop=True, authorization=True, context="eyJsb2NhdGlvbiI6IlVzZXIgUHJvZmlsZSJ9"),
                    json={}
                )
                if "You are being rate limited." in r.text:
                    self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{r.json()['retry_after']} seconds{self.c.clnt.white}.")
                    time.sleep(r.json()["retry_after"])
                else:
                    break
            
            if r.status_code == 204:
                if user in self.outgoing:
                    self.outgoing_added += 1
                    self.c.success(f"Sent request: {self.c.clnt.maincol}{user}{self.c.clnt.white} ({self.c.clnt.maincol}Outgoing{self.c.clnt.white})")
                elif user in self.incoming:
                    self.incoming_added += 1
                    self.c.success(f"Sent request: {self.c.clnt.maincol}{user}{self.c.clnt.white} ({self.c.clnt.maincol}Incoming{self.c.clnt.white})")
                else:
                    self.friends_added += 1
                    self.c.success(f"Sent request: {self.c.clnt.maincol}{user}{self.c.clnt.white} ({self.c.clnt.maincol}Friend{self.c.clnt.white})")
            else:
                if user in self.outgoing:
                    self.c.fail(f"Couldn't send request: {self.c.clnt.maincol}{user}{self.c.clnt.white} ({self.c.clnt.maincol}Outgoing{self.c.clnt.white})")
                elif user in self.incoming:
                    self.c.fail(f"Couldn't send request: {self.c.clnt.maincol}{user}{self.c.clnt.white} ({self.c.clnt.maincol}Incoming{self.c.clnt.white})")
                else:
                    self.c.fail(f"Couldn't send request: {self.c.clnt.maincol}{user}{self.c.clnt.white} ({self.c.clnt.maincol}Friend{self.c.clnt.white})")

            wait = random.randint(5,7)
            self.c.warn(f"Sleeping {wait} seconds.")
            time.sleep(wait)

        for user in self.to_block:
            while True: # get user from id
                r = requests.put(f"https://discord.com/api/v9/users/@me/relationships/{user}",
                    headers = self._headers("put", debugoptions=True, discordlocale=True, superprop=True, authorization=True, context="eyJsb2NhdGlvbiI6IlVzZXIgUHJvZmlsZSJ9"),
                    json={"type":2}
                )
                if "You are being rate limited." in r.text:
                    self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{r.json()['retry_after']} seconds{self.c.clnt.white}.")
                    time.sleep(int(r.json()["retry_after"]) / 1000)
                else:
                    break
            
            if r.status_code == 204:
                self.c.success(f"Blocked: {self.c.clnt.maincol}{user}{self.c.clnt.white}")
                self.blocked_added += 1
            else:
                self.c.fail(f"Couldn't block: {self.c.clnt.maincol}{user}{self.c.clnt.white}")
            
            wait = random.randint(5,7)
            self.c.warn(f"Sleeping {wait} seconds.")
            time.sleep(wait)

    def user_data(self):
        time_now = int(time.time())
        f = open(f"pfp-{time_now}.png", "wb")
        f.write(base64.b64decode(self.restore_data['avatar-bytes']))
        f.close()
        self.c.success(f"Saved avatar: {self.c.clnt.maincol}pfp-{time_now}.png")
        
        f = open(f"bio-{time_now}.txt", "w", encoding="utf-8")
        f.write(self.restore_data['bio'])
        f.close()
        self.c.success(f"Saved bio: {self.c.clnt.maincol}bio-{time_now}.txt")

        if self.restore_data['banner-bytes'] != "":
            f = open(f"banner-{time_now}.gif", "wb")
            f.write(base64.b64decode(self.restore_data['banner-bytes']))
            f.close()
            self.c.success(f"Saved banner: {self.c.clnt.maincol}banner-{time_now}.gif")
    
    def folders(self):
        while True:
            user_guilds_req = requests.get(f"https://discord.com/api/v9/users/@me/guilds",
                headers=self._headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=True)
            )
            if "You are being rate limited." in r.text:
                self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{r.json()['retry_after']} seconds{self.c.clnt.white}.")
                time.sleep(r.json()["retry_after"])
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
            r = requests.patch(f"https://discord.com/api/v9/users/@me/settings",
                headers = self._headers("patch", debugoptions=True, discordlocale=True, superprop=True, authorization=True),
                json = {"guild_folders": data_to_send}
            )
            if "You are being rate limited." in r.text:
                self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{r.json()['retry_after']} seconds{self.c.clnt.white}.")
                time.sleep(r.json()["retry_after"])
            else:
                break

        if r.status_code == 200:
            self.c.success(f"Restored Guild Folders")
        else:
            self.c.fail(f"Couldn't Restore Guild Folders: {self.c.clnt.maincol}{r.status_code}")