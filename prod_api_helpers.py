import json
import prod_config
import requests
from time import sleep

homepage_url = "https://github.com/MerelyMezz/prod_discord_bot"
version = "1"
api_version = 10
ApiURL = "https://discord.com/api/v{}".format(api_version)

GuildId = prod_config.GetConfigString("Guild")
BotToken = prod_config.GetConfigString("BotToken")
LogChannel = prod_config.GetConfigString("LogChannel")
QuarantineRole = prod_config.GetConfigString("QuarantineRole")

Headers = {"Authorization":"Bot {}".format(BotToken),
           "User-Agent": "DiscordBot ({}, {})".format(homepage_url, version),
           "Content-Type": "application/json"
}

# Helper functions
def Api_Request(request_type, api_string, body=None):
    if not request_type in ["get", "post", "put", "delete"]:
        print("Invalid request type: {}".format(request_type))
        exit(1)

    while True:
        Response = getattr(requests, request_type)(ApiURL + api_string, headers = Headers, data=body)
        content = json.loads(Response.content) if Response.status_code != 204 else None
        if Response.status_code == 429:
            sleep(content["retry_after"])
        else:
            break

    return content, Response.status_code

def PostMessage(channel_id, message):
    message_json = json.dumps({"content": message})
    Api_Request("post", "/channels/{}/messages".format(channel_id), message_json)

def PostLogMessage(message):
    PostMessage(LogChannel, message)

def DeleteMessage(message_data):
    response_code = Api_Request("delete", "/channels/{}/messages/{}".format(message_data["channel_id"], message_data["id"]))[1]

    if response_code == 204:
        PostLogMessage("Deleted message from <@{}>:\n```{}```".format(message_data["author"]["id"], message_data["content"]))

def QuarantineUser(user_id, reason):
    Api_Request("put", "/guilds/{}/members/{}/roles/{}".format(GuildId, user_id, QuarantineRole))
    PostLogMessage("Quarantined user <@{}>: `{}`".format(user_id, reason))

SelfID = Api_Request("get", "/users/@me")[0]["id"]
