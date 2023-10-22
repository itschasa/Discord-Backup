# Copyright (C) 2021 github.com/ItsChasa
#
# This source code has been released under the GNU Affero General Public
# License v3.0. A copy of this license is available at
# https://www.gnu.org/licenses/agpl-3.0.en.html

import base64
import time
import json
import os
from datetime import datetime

import console
from main import request_client, colours, config
from client_info import build_headers

class backup():
    def __init__(self, token, c: console.prnt, version) -> None:
        self.backup_data = {"version": version}
        self.before = time.time()
        self.token = token
        self.fatal_error = False
        self.c = c

        token_check = request_client.get("https://discord.com/api/v9/users/@me",
            headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True)
        )
        if token_check.status_code != 200:
            self.fatal_error = "Invalid Token"
        else:
            self.user_me = token_check.json()
            self.user_info()
            self.relationships()
            self.get_favourite_gifs()
            self.guilds()
            print()
            self.group_chats()
            print()
            self.dm_history()
            print()
            
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
            self.c.info(f"User Info + Avatar: {colours['main_colour']}Done")
            self.c.info(f"Guild Folders: {colours['main_colour']}Done")
            self.c.info(f"Favourited GIFs: {colours['main_colour']}Done")
            self.c.info(f"Guilds: {colours['main_colour']}{guild1}/{guild2}")
            self.c.info(f"Group Chats: {colours['main_colour']}{self.gc_success}/{self.gc_success + self.gc_fail}")

            if len(self.g_failed) != 0:
                self.c.warn(f"Failed Guilds:")
                for guild in self.g_failed:
                    self.c.warn(f"{guild['name']}", indent=2)

            self.c.info(f"Relationships:")
            self.c.info(f"Friends: {colours['main_colour']}{len(self.backup_data['friends'])}", indent=2)
            self.c.info(f"Blocked: {colours['main_colour']}{len(self.backup_data['blocked'])}", indent=2)
            self.c.info(f"Incoming: {colours['main_colour']}{len(self.backup_data['incoming'])}", indent=2)
            self.c.info(f"Outgoing: {colours['main_colour']}{len(self.backup_data['outgoing'])}", indent=2)
            self.c.info(f"DM Historys: {colours['main_colour']}{len(self.dm_historys)}", indent=2)
            self.c.info(f"Time Elapsed: {colours['main_colour']}{self._show_time(int(self.after - self.before))}")
    
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
        self.c.success(f"Backed up: {colours['main_colour']}User Info")

        r = request_client.get(f"https://cdn.discordapp.com/avatars/{self.backup_data['id']}/{self.user_me['avatar']}", headers=build_headers("get"))
        base64_bytes = base64.b64encode(r.content)
        base64_message = base64_bytes.decode('ascii')
        self.backup_data["avatar-bytes"] = base64_message
        self.c.success(f"Backed up: {colours['main_colour']}Avatar")

        r = request_client.get(f"https://cdn.discordapp.com/banners/{self.backup_data['id']}/{self.user_me['banner']}", headers=build_headers("get"))
        base64_bytes = base64.b64encode(r.content)
        base64_message = base64_bytes.decode('ascii')
        self.backup_data["banner-bytes"] = base64_message
        self.c.success(f"Backed up: {colours['main_colour']}Banner")

        r = request_client.get(f"https://discord.com/api/v9/users/@me/settings", headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True))
        settings = r.json()
        self.backup_data["guild_folders"] = settings["guild_folders"]
        self.c.success(f"Backed up: {colours['main_colour']}Guild Folders")
    
    def group_chats(self):
        while True:
            r = request_client.get(f"https://discord.com/api/v9/users/@me/channels", headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True))
            if "You are being rate limited." in r.text:
                self.c.warn(f"Rate Limited: {colours['main_colour']}{r.json()['retry_after']} seconds{colours['white']}.")
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
            self.c.info(f"[{colours['main_colour']}{channels.index(channel) + 1}/{len(channels)}{colours['white']}] Creating invite for {colours['main_colour']}{channel['name']}{colours['white']} ({colours['main_colour']}{len(channel['recipients'])} users{colours['white']}):")
            time_since_last_msg = time.time() - self._reverse_snowflake(channel['last_message_id'])
            
            if int(config.group_chat_msg) != 0:
                if time_since_last_msg > int(config.group_chat_msg):
                    self.c.warn(f"Group Chat too old ({colours['main_colour']}{self._show_time(time_since_last_msg)} since last message{colours['white']})", indent=2)
                    continue
            
            while True:
                r = request_client.post(f"https://discord.com/api/v9/channels/{channel['id']}/invites", 
                    json={
                        "max_age": 604800
                    }, 
                    headers=build_headers("post", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token)
                )
                if "You are being rate limited." in r.text or r.status_code == 429:
                    self.c.warn(f"Rate Limited: {colours['main_colour']}{(r.json()['retry_after'])} seconds{colours['white']}.", indent=2)
                    time.sleep((r.json()["retry_after"]) + 0.3)
                else:
                    if r.status_code == 200:
                        code = r.json()['code']
                        self.c.success(f"Created Invite | {colours['main_colour']}{code}", indent=2)
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
            r = request_client.get(f"https://discord.com/api/v9/users/@me/relationships", headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True))
            if "You are being rate limited." in r.text:
                self.c.warn(f"Rate Limited: {colours['main_colour']}{r.json()['retry_after']} seconds{colours['white']}.")
                time.sleep((int(r.json()["retry_after"]) + 0.3))
            else:
                break
        friend_data = r.json()

        relationship_map = {
            1: [],
            2: [],
            3: [],
            4: []
        }

        for user in friend_data:
            if user["type"] in relationship_map:
                relationship_map[user["type"]].append(user["id"])

        self.backup_data["friends"] = relationship_map[1]
        self.backup_data["blocked"] = relationship_map[2]
        self.backup_data["incoming"] = relationship_map[3]
        self.backup_data["outgoing"] = relationship_map[4]

        self.c.success(f"Backed up: {colours['main_colour']}Relationships")

    def _get_invite(self, guild):
        while True:
            r = request_client.get(f"https://discord.com/api/v9/guilds/{guild['id']}/channels", headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True))
            if "You are being rate limited." in r.text:
                self.c.warn(f"Rate Limited: {colours['main_colour']}{(r.json()['retry_after'])} seconds{colours['white']}.", indent=2)
                time.sleep((r.json()["retry_after"]) + 0.3)
            else:
                break
        
        channels = r.json()

        invite_payload = {
            'max_age': 2592000 if 'COMMUNITY' not in guild['features'] else 0,
            'max_uses': 0,
            'target_type': None,
            'target_user_id': None,
            'temporary': False,
            'validate': None,
        }

        invite_headers = build_headers("post", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True)

        words = ["general", "rules", "news", "txt"]
        allowed_channel_types = [0,2,3,5,13]
        done, code = False, False
        error = 0
        retries = 5

        for channel in channels:
            if channel["type"] not in allowed_channel_types:
                channels.remove(channel)

        for channel in channels:
            if done is not False or error >= retries:
                break
            for word in words:
                if done is not False or error >= retries:
                    break
                if word in channel['name']:
                    while True:
                        r = request_client.post(f"https://discord.com/api/v9/channels/{channel['id']}/invites", 
                            json = invite_payload, 
                            headers = invite_headers
                        )
                        if "You are being rate limited." in r.text or r.status_code == 429:
                            self.c.warn(f"Rate Limited: {colours['main_colour']}{(r.json()['retry_after'])} seconds{colours['white']}.", indent=2)
                            time.sleep((r.json()["retry_after"]) + 0.3)
                        else:
                            if r.status_code == 200:
                                done = code = r.json()['code']
                                self.c.success(f"Created Invite in {colours['main_colour']}#{channel['name']}{colours['white']} | {colours['main_colour']}{code}", indent=2)
                                break
                            else:
                                error += 1
                                self.c.fail(f"Can't Create Invite in {colours['main_colour']}#{channel['name']}{colours['white']} ({colours['main_colour']}{error}/{retries}{colours['white']})", indent=2)
                                break
        
        if done is False:
            for channel in channels:
                if done != False or error >= retries:
                    break
                while True:
                    r = request_client.post(f"https://discord.com/api/v9/channels/{channel['id']}/invites", 
                        
                        json={
                            "max_age": 0,
                            "max-uses": 0,
                            "temporary": False
                        }, 
                        
                        headers=build_headers("post", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token)
                    )
                    if "You are being rate limited." in r.text or r.status_code == 429:
                        self.c.warn(f"Rate Limited: {colours['main_colour']}{(r.json()['retry_after'])} seconds{colours['white']}.", indent=2)
                        time.sleep((r.json()["retry_after"]) + 0.3)
                    else:
                        if r.status_code == 200:
                            done = code = r.json()['code']
                            self.c.success(f"Created Invite in {colours['main_colour']}#{channel['name']}{colours['white']} | {colours['main_colour']}{code}", indent=2)
                            break
                        else:
                            error += 1
                            self.c.fail(f"Can't Create Invite in {colours['main_colour']}#{channel['name']} {colours['white']}({colours['main_colour']}{error}/{retries}{colours['white']})", indent=2)
                            break
        return code, done

    def guilds(self):
        r = request_client.get(f"https://discord.com/api/v9/users/@me/guilds", headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True))
        guilds = r.json()

        self.guild_list = []
        self.g_codes = []
        self.g_failed = []


        for guild in guilds:
            self.c.info(f"[{colours['main_colour']}{guilds.index(guild) + 1}/{len(guilds)}{colours['white']}] Creating invite for {colours['main_colour']}{guild['name']}{colours['white']}:")
            if "VANITY_URL" in guild["features"]:
                while True:
                    r = request_client.get(f"https://discord.com/api/v9/guilds/{guild['id']}", headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True))
                    if "You are being rate limited." in r.text:
                        self.c.warn(f"Rate Limited: {colours['main_colour']}{(r.json()['retry_after'])} seconds{colours['white']}.", indent=2)
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
                        self.c.success(f"Using {colours['main_colour']}Vanity Url{colours['white']} as invite. | {colours['main_colour']}{code}", indent=2)
                        done = True

            else:
                code, done = self._get_invite(guild)
                
            if done is False:
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

        self.c.success(f"Backed up: {colours['main_colour']}Users DMed")
    
    def get_favourite_gifs(self):
        r = request_client.get('https://discord.com/api/v9/users/@me/settings-proto/2', headers=build_headers("get", debugoptions=True, discordlocale=True, superprop=True, authorization=self.token, timezone=True))
        if r.status_code == 200:
            self.backup_data['settings'] = r.json()['settings']
            self.c.success(f"Backed up: {colours['main_colour']}Favourited GIFs")
            return 'Done'
        else:
            self.c.fail(f"Couldn't back up: {colours['main_colour']}Favourited GIFs ({r.status_code})")
            return 'Failed'
