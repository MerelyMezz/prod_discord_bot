import prod_api_helpers

ModuleFunctions = {}
ModuleFunctions["MESSAGE_CREATE"] = {"BlockAtEveryone"}

def BlockAtEveryone(d):
    if not d["mention_everyone"] == True:
        return

    prod_api_helpers.QuarantineUser(d["author"]["id"], "Posted an @everyone mention")
    prod_api_helpers.DeleteMessage(d)