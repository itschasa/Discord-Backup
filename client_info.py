# -*- coding: utf-8 -*-
# Copyright (C) 2021 github.com/ItsChasa
#
# This source code has been released under the GNU Affero General Public
# License v3.0. A copy of this license is available at
# https://www.gnu.org/licenses/agpl-3.0.en.html

import base64
import re
import json
import traceback
import time
import tls_client

# browser data
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
sec_ch_ua = '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"'
browser_version = "113.0.0.0"
request_client_identifier = "chrome_113" # tls_client uses this to determine what "Client Hello" to use

request_client = tls_client.Session(
    client_identifier=request_client_identifier,
    random_tls_extension_order=True
)

# discord data
def get_client_build_number():
    global discord_build_failback
    try:
        login_page_request = request_client.get('https://discord.com/login', headers={"Accept-Encoding": "identity"})
        login_page = login_page_request.text
        build_url = 'https://discord.com/assets/' + re.compile(r'assets/(sentry\.\w+)\.js').findall(login_page)[0] + '.js'
        build_request = request_client.get(build_url, headers={"Accept-Encoding": "identity"})
        build_nums = re.findall(r'buildNumber\D+(\d+)"', build_request.text)
        return int(build_nums[0])
    
    except:
        traceback.print_exc()
        print("Failed to get build number from Discord, failing back to hardcoded value...")
        time.sleep(2)
        discord_build_failback = True
        return 254206

discord_build_failback = False
discord_build = get_client_build_number()
super_properties = {
    "os": "Windows",
    "browser": "Chrome",
    "device": "",
    "system_locale": "en-US",
    "browser_user_agent": user_agent,
    "browser_version": browser_version,
    "os_version": "10",
    "referrer": "",
    "referring_domain": "",
    "referrer_current": "",
    "referring_domain_current": "",
    "release_channel": "stable",
    "client_build_number": discord_build,
    "client_event_source": None
}
b64_super_properties = base64.b64encode(json.dumps(super_properties, separators=(',', ':')).encode()).decode()


def build_headers(
    method,
    superprop=False,
    debugoptions=False,
    discordlocale=False,
    authorization=False,
    origin=False,
    referer="https://discord.com/channels/@me", 
    context=False,
    timezone=False
):
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "locale=en-GB",
        "Referer": referer,
        "Sec-Ch-Ua": sec_ch_ua,
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": user_agent
    }

    if referer is False:
        del headers["Referer"]
    
    if method != "get":
        headers["Content-Type"] = "application/json"
        if origin is not False:
            headers["Origin"] = origin

    if authorization is not False:
        headers["Authorization"] = authorization
    if debugoptions is True:
        headers["X-Debug-Options"] = "bugReporterEnabled"
    if discordlocale is True:
        headers["X-Discord-Locale"] = "en-US"
    if superprop is True:
        headers["X-Super-Properties"] = b64_super_properties
    if context is True:
        headers["X-Context-Properties"] = context
    if timezone is True:
        headers["X-Discord-Timezone"] = "Europe/London"
    
    keyssorted = sorted(headers.keys(), key=lambda x:x.lower())
    newheaders={}
    for key in keyssorted:
        newheaders[key] = headers[key]

    return headers
