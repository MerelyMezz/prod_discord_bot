import prod_api_helpers
import re

ModuleFunctions = {}
ModuleFunctions["MESSAGE_CREATE"] = {"BlockMarkdownLinks"}

def BlockMarkdownLinks(d):
    if re.search("\\[.*\\]\\(http(s)?://.*\\)", d["content"]) == None:
        return

    prod_api_helpers.QuarantineUser(d["author"]["id"], "Posted a markdown link")
    prod_api_helpers.DeleteMessage(d)