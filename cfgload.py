# -*- coding: utf-8 -*-
# Copyright (C) 2021 github.com/ItsChasa
#
# This source code has been released under the GNU Affero General Public
# License v3.0. A copy of this license is available at
# https://www.gnu.org/licenses/agpl-3.0.en.html

import yaml

class Config():
    "Ex: `config.threads`"
    def __init__(self) -> None:
        data = yaml.safe_load(open("config.yml"))
        
        self.colour = data['colour']
        self.group_chat_msg = data['group_chat_msg']