# -*- coding: utf-8 -*-
# Copyright (C) 2021 github.com/ItsChasa
#
# This source code has been released under the GNU Affero General Public
# License v3.0. A copy of this license is available at
# https://www.gnu.org/licenses/agpl-3.0.en.html

import startup

class prnt():
    def __init__(self, clnt : startup.Setup) -> None:
        self.clnt = clnt
    
    def success(self, content, end="\n", indent=0):
        ind = ""
        for _ in range(indent): ind += " "
        print(f"{ind}{self.clnt.green}>{self.clnt.white} {content}", end=end)
    
    def info(self, content, end="\n", indent=0):
        ind = ""
        for _ in range(indent): ind += " "
        print(f"{ind}{self.clnt.white}> {content}", end=end)
    
    def fail(self, content, end="\n", indent=0):
        ind = ""
        for _ in range(indent): ind += " "
        print(f"{ind}{self.clnt.red}>{self.clnt.white} {content}", end=end)
    
    def inp(self, content, end="\n", indent=0):
        ind = ""
        for _ in range(indent): ind += " "
        print(f"{ind}{self.clnt.blue}>{self.clnt.white} {content}", end=end)
    
    def warn(self, content, end="\n", indent=0):
        ind = ""
        for _ in range(indent): ind += " "
        print(f"{ind}{self.clnt.yellow}>{self.clnt.white} {content}", end=end)