# Copyright (C) 2021 github.com/ItsChasa
#
# This source code has been released under the GNU Affero General Public
# License v3.0. A copy of this license is available at
# https://www.gnu.org/licenses/agpl-3.0.en.html

import base64, requests, time, json, os
from datetime import datetime

import console

class backup():
    def __init__(self, token, c: console.prnt, version) -> None:
        self.backup_data = {"version": version}
        self.before = time.time()
        self.token = token
        self.fatal_error = False
        self.c = c

        token_check = requests.get("https://discord.com/api/v9/users/@me", headers=self._headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=True))
        if token_check.status_code != 200:
            self.fatal_error = "Invalid Token"
        else:
            self.user_me = token_check.json()
            self.user_info()
            self.relationships()
            self.guilds()
            print()
            self.group_chats()
            print()
            self.dm_history()
            
            if not os.path.exists('backups'):
                os.makedirs('backups')

            f = open(f"backups\\{self.user_me['username']}#{self.user_me['discriminator']} @ {datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-%d %H-%M-%S')}.bkup", "w", encoding="utf-8")
            f.write(json.dumps(self.backup_data, indent=4))
            f.close()

            guild1 = 0
            guild2 = 0

            for code in self.g_codes:
                if code != "Unable to create.":
                    guild1 += 1
                guild2 += 1

            self.after = time.time()

            print()
            self.c.success(f"Backup Complete!")
            self.c.info(f"User Info + Avatar: {self.c.clnt.maincol}Done")
            self.c.info(f"Guild Folders: {self.c.clnt.maincol}Done")
            self.c.info(f"Guilds: {self.c.clnt.maincol}{guild1}/{guild2}")
            self.c.info(f"Group Chats: {self.c.clnt.maincol}{self.gc_success}/{self.gc_success + self.gc_fail}")

            if len(self.g_failed) != 0: self.c.warn(f"Failed Guilds:")
            for guild in self.g_failed: self.c.warn(f"{guild['name']}", indent=2)

            self.c.info(f"Relationships:")
            self.c.info(f"Friends: {self.c.clnt.maincol}{len(self.friends)}", indent=2)
            self.c.info(f"Blocked: {self.c.clnt.maincol}{len(self.blocked)}", indent=2)
            self.c.info(f"Incoming: {self.c.clnt.maincol}{len(self.incoming)}", indent=2)
            self.c.info(f"Outgoing: {self.c.clnt.maincol}{len(self.outgoing)}", indent=2)
            self.c.info(f"DM Historys: {self.c.clnt.maincol}{len(self.dm_historys)}", indent=2)
            self.c.info(f"Time Elapsed: {self.c.clnt.maincol}{self._show_time(int(self.after - self.before))}")


    
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

        if authorization is True:
            headers["Authorization"] = self.token
        if origin != False:
            headers["Origin"] = origin
        if debugoptions is True:
            headers["X-Debug-Options"] = "bugReporterEnabled"
        if discordlocale is True:
            headers["X-Discord-Locale"] = "en-US"
        if superprop is True:
            headers["X-Super-Properties"] = "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMC4wLjQ4OTYuMTI3IFNhZmFyaS81MzcuMzYiLCJicm93c2VyX3ZlcnNpb24iOiIxMDAuMC40ODk2LjEyNyIsIm9zX3ZlcnNpb24iOiIxMCIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoxMjY0NjIsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
        if context != False:
            headers["X-Context-Properties"] = context
        
        keyssorted = sorted(headers.keys(), key=lambda x:x.lower())
        newheaders={}
        for key in keyssorted:
            newheaders[key] = headers[key]

        return headers
    
    def _reverse_snowflake(self, snfk):
        try:
            x = bin(int(snfk)).replace("0b", "")
            for _ in range(64 - len(x)): x = "0" + x
            x = (int(x[:42], 2) + 1420070400000) / 1000
            return x
        except:
            return 0

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

    def user_info(self):
        self.backup_data["name"] = self.user_me['username']
        self.backup_data["discriminator"] = str(self.user_me['discriminator'])
        self.backup_data["id"] = str(self.user_me["id"])
        self.backup_data["bio"] = self.user_me["bio"]
        self.c.success(f"Backed up: {self.c.clnt.maincol}User Info")

        r = requests.get(f"https://cdn.discordapp.com/avatars/{self.backup_data['id']}/{self.user_me['avatar']}")
        base64_bytes = base64.b64encode(r.content)
        base64_message = base64_bytes.decode('ascii')
        self.backup_data["avatar-bytes"] = base64_message
        self.c.success(f"Backed up: {self.c.clnt.maincol}Avatar")

        r = requests.get(f"https://cdn.discordapp.com/banners/{self.backup_data['id']}/{self.user_me['banner']}")
        base64_bytes = base64.b64encode(r.content)
        base64_message = base64_bytes.decode('ascii')
        self.backup_data["banner-bytes"] = base64_message
        self.c.success(f"Backed up: {self.c.clnt.maincol}Banner")

        r = requests.get(f"https://discord.com/api/v9/users/@me/settings", headers=self._headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=True))
        settings = r.json()
        self.backup_data["guild_folders"] = settings["guild_folders"]
        self.c.success(f"Backed up: {self.c.clnt.maincol}Guild Folders")
    
    def group_chats(self):
        while True:
            r = requests.get(f"https://discord.com/api/v9/users/@me/channels", headers=self._headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=True))
            if "You are being rate limited." in r.text:
                self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{r.json()['retry_after']} seconds{self.c.clnt.white}.")
                time.sleep((int(r.json()["retry_after"]) + 0.3))
            else:
                break
        
        channels = r.json()
        self.channels = channels
        new_channels = r.json()
        for chn in channels:
            if chn['type'] != 3:
                new_channels.remove(chn)
        
        channels = new_channels

        self.gc_success = self.gc_fail = 0
        self.backup_data['group-chats'] = []

        for channel in channels:
            self.c.info(f"[{self.c.clnt.maincol}{channels.index(channel) + 1}/{len(channels)}{self.c.clnt.white}] Creating invite for {self.c.clnt.maincol}{channel['name']}{self.c.clnt.white} ({self.c.clnt.maincol}{len(channel['recipients'])} users{self.c.clnt.white}):")
            time_since_last_msg = time.time() - self._reverse_snowflake(channel['last_message_id'])
            
            if int(self.c.clnt.cfg.group_chat_msg) != 0:
                if time_since_last_msg > int(self.c.clnt.cfg.group_chat_msg):
                    self.c.warn(f"Group Chat too old ({self.c.clnt.maincol}{self._show_time(time_since_last_msg)} since last message{self.c.clnt.white})", indent=2)
                    continue
            
            while True:
                r = requests.post(f"https://discord.com/api/v9/channels/{channel['id']}/invites", 
                
                json={
                    "max_age": 604800
                }, 
                
                headers=self._headers("post", debugoptions=True, discordlocale=True, superprop=True, authorization=True)
                )
                if "You are being rate limited." in r.text or r.status_code == 429:
                    self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{(r.json()['retry_after'])} seconds{self.c.clnt.white}.", indent=2)
                    time.sleep((r.json()["retry_after"]) + 0.3)
                else:
                    if r.status_code == 200:
                        code = r.json()['code']
                        self.c.success(f"Created Invite | {self.c.clnt.maincol}{code}", indent=2)
                        self.backup_data['group-chats'].append({"name": channel['name'], "id": channel['id'], "invite-code": r.json()['code']})
                        self.gc_success += 1
                        break
                    else:
                        self.c.fail(f"Can't Create Invite", indent=2)
                        self.backup_data['group-chats'].append({"name": channel['name'], "id": channel['id'], "invite-code": "Unable to create."})
                        self.gc_fail += 1
                        break
        


    def relationships(self):
        while True:
            r = requests.get(f"https://discord.com/api/v9/users/@me/relationships", headers=self._headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=True))
            if "You are being rate limited." in r.text:
                self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{r.json()['retry_after']} seconds{self.c.clnt.white}.")
                time.sleep((int(r.json()["retry_after"]) + 0.3))
            else:
                break
        friend_data = r.json()

        self.friends = []
        self.blocked = []
        self.outgoing = []
        self.incoming = []

        for user in friend_data:
            if user["type"] == 1:
                self.friends.append(user["id"])
            elif user["type"] == 2:
                self.blocked.append(user["id"])
            elif user["type"] == 3:
                self.incoming.append(user["id"])
            elif user["type"] == 4:
                self.outgoing.append(user["id"])

        self.backup_data["friends"] = self.friends
        self.backup_data["blocked"] = self.blocked
        self.backup_data["incoming"] = self.incoming
        self.backup_data["outgoing"] = self.outgoing

        self.c.success(f"Backed up: {self.c.clnt.maincol}Relationships")

    def _get_invite(self, guild):
        while True:
            r = requests.get(f"https://discord.com/api/v9/guilds/{guild['id']}/channels", headers=self._headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=True))
            if "You are being rate limited." in r.text:
                self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{(r.json()['retry_after'])} seconds{self.c.clnt.white}.", indent=2)
                time.sleep((r.json()["retry_after"]) + 0.3)
            else:
                break
        
        channels = r.json()

        words = ["general", "rules", "news", "txt"]
        allowed_channel_types = [0,2,3,5,13]
        done = code = False
        error = 0
        retries = 3

        for channel in channels:
            if channel["type"] not in allowed_channel_types:
                channels.remove(channel)

        for channel in channels:
            if done != False or error >= retries:
                break
            for word in words:
                if done != False or error >= retries:
                    break
                if word in channel['name']:
                    while True:
                        r = requests.post(f"https://discord.com/api/v9/channels/{channel['id']}/invites", 
                        
                        json={
                            "max_age": 0,
                            "max-uses": 0,
                            "temporary": False
                        }, 
                        
                        headers=self._headers("post", debugoptions=True, discordlocale=True, superprop=True, authorization=True)
                        )
                        if "You are being rate limited." in r.text or r.status_code == 429:
                            self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{(r.json()['retry_after'])} seconds{self.c.clnt.white}.", indent=2)
                            time.sleep((r.json()["retry_after"]) + 0.3)
                        else:
                            if r.status_code == 200:
                                done = code = r.json()['code']
                                self.c.success(f"Created Invite in {self.c.clnt.maincol}#{channel['name']}{self.c.clnt.white} | {self.c.clnt.maincol}{code}", indent=2)
                                break
                            else:
                                error += 1
                                self.c.fail(f"Can't Create Invite in {self.c.clnt.maincol}#{channel['name']}{self.c.clnt.white} ({self.c.clnt.maincol}{error}/3{self.c.clnt.white})", indent=2)
                                break
        
        if done == False:
            for channel in channels:
                if done != False or error >= retries:
                    break
                while True:
                    r = requests.post(f"https://discord.com/api/v9/channels/{channel['id']}/invites", 
                        
                        json={
                            "max_age": 0,
                            "max-uses": 0,
                            "temporary": False
                        }, 
                        
                        headers=self._headers("post", debugoptions=True, discordlocale=True, superprop=True, authorization=True)
                    )
                    if "You are being rate limited." in r.text or r.status_code == 429:
                        self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{(r.json()['retry_after'])} seconds{self.c.clnt.white}.", indent=2)
                        time.sleep((r.json()["retry_after"]) + 0.3)
                    else:
                        if r.status_code == 200:
                            done = code = r.json()['code']
                            self.c.success(f"Created Invite in {self.c.clnt.maincol}#{channel['name']}{self.c.clnt.white} | {self.c.clnt.maincol}{code}", indent=2)
                            break
                        else:
                            error += 1
                            self.c.fail(f"Can't Create Invite in {self.c.clnt.maincol}#{channel['name']} {self.c.clnt.white}({self.c.clnt.maincol}{error}/3{self.c.clnt.white})", indent=2)
                            break
        return code, done

    def guilds(self):
        r = requests.get(f"https://discord.com/api/v9/users/@me/guilds", headers=self._headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=True))
        guilds = r.json()

        self.guild_list = []
        self.g_codes = []
        self.g_failed = []


        for guild in guilds:
            self.c.info(f"[{self.c.clnt.maincol}{guilds.index(guild) + 1}/{len(guilds)}{self.c.clnt.white}] Creating invite for {self.c.clnt.maincol}{guild['name']}{self.c.clnt.white}:")
            if "VANITY_URL" in guild["features"]:
                while True:
                    r = requests.get(f"https://discord.com/api/v9/guilds/{guild['id']}", headers=self._headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=True))
                    if "You are being rate limited." in r.text:
                        self.c.warn(f"Rate Limited: {self.c.clnt.maincol}{(r.json()['retry_after'])} seconds{self.c.clnt.white}.", indent=2)
                        time.sleep((r.json()["retry_after"]) + 0.3)
                    else:
                        break
                try:
                    code = r.json()["vanity_url_code"]
                except:
                    code, done = self._get_invite(guild)
                else:
                    if code == None:
                        code, done = self._get_invite(guild)
                    else:
                        self.c.success(f"Using {self.c.clnt.maincol}Vanity Url{self.c.clnt.white} as invite. | {self.c.clnt.maincol}{code}", indent=2)
                        done = True

            else:
                code, done = self._get_invite(guild)
                
            if done == False:
                code = "Unable to create."
            
            self.guild_list.append({
                "name": guild['name'],
                "id": guild['id'],
                "invite-code": code
            })
            
            self.g_codes.append(code)

            if code == "Unable to create.":
                self.g_failed.append({"name": guild["name"], "id": guild["id"]})

        self.backup_data["guilds"] = self.guild_list
    
    def dm_history(self):
        dms = []

        for chan in self.channels:
            if chan['type'] == 1:
                dms.append(
                    {
                        "user_id": chan['recipients'][0]['id'],
                        "last_message_id": chan['last_message_id'],
                        "user": f"{chan['recipients'][0]['username']}#{chan['recipients'][0]['discriminator']}",
                        "timestamp": int(self._reverse_snowflake(chan['last_message_id']))
                    }
                )

        def extract_id(js):
            try:
                return int(js['last_message_id'])
            except TypeError:
                return 0

        dms.sort(key=extract_id, reverse=True)
                
        self.backup_data['dm-history'] = dms
        self.dm_historys = dms

        self.c.success(f"Backed up: {self.c.clnt.maincol}Users DMed")
