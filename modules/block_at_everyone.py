import prod_api_helpers
import re

ModuleFunctions = {}
ModuleFunctions["MESSAGE_CREATE"] = {"BlockAtEveryone"}
ModuleFunctions["MESSAGE_UPDATE"] = {"BlockAtEveryone"}

def BlockAtEveryone(d):
    if re.search("@everyone", d["content"]) == None:
        return

    prod_api_helpers.QuarantineUser(d["author"]["id"], "Posted an @everyone mention")
    prod_api_helpers.DeleteMessage(d)