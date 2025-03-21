#!/usr/bin/env python3

import asyncio
import importlib
import json
import os
import platform
from pprint import pprint
import prod_api_helpers
import prod_config
import random
import signal
import threading
from time import sleep
import websockets

signal.signal(signal.SIGINT, lambda n,m: os._exit(1))

# intents
# https://discord.com/developers/docs/events/gateway#list-of-intents

Intents = [
    9,  #GUILD_MESSAGES
    15  #MESSAGE_CONTENT
]

# opcodes
#https://discord.com/developers/docs/topics/opcodes-and-status-codes#gateway-gateway-opcodes

class OPCode:
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    HELLO = 10
    HEARTBEAT_ACK = 11

# Set up table to call functions for events
EventHooks = {}

module_entries = prod_config.GetConfigFilteredDictArray("EnableModule", "True")
Modules = list(map(lambda x: importlib.import_module("modules.{}".format(x[0:-3])), filter(lambda x: x[-3:] == ".py" and x[0:-3] in module_entries, os.listdir("modules"))))

for module in Modules:
    for event_name in module.ModuleFunctions.keys():
        EventHooks[event_name] = EventHooks[event_name] if event_name in EventHooks.keys() else set()
        ModuleFunctions = map(lambda x: getattr(module,x), module.ModuleFunctions[event_name])
        EventHooks[event_name] = EventHooks[event_name].union(ModuleFunctions)

# Main web socket loop from which we receive events
GatewayURL = prod_api_helpers.Api_Request("get", "/gateway")[0]["url"]

HeartbeatThread = None
LoopRestartEvent = threading.Event()

async def WebSocketLoop():
    wss_url = "{}/?v={}&encoding=json".format(GatewayURL, prod_api_helpers.api_version)
    async with websockets.connect(wss_url) as ws:
        async def Send(dict):
            await ws.send(json.dumps(dict))

        async def Receive():
            return json.loads(await ws.recv())

        # Receive initial event
        hello_event = await Receive()

        if hello_event["op"] != OPCode.HELLO:
            print("Bad Hello event from websocket")
            exit(1)

        HeartbeatInterval = hello_event["d"]["heartbeat_interval"] * 0.001

        # start heartbeat loop
        async def HeartbeatLoop():
            LoopRestartEvent.wait(random.uniform(0.1, HeartbeatInterval))
            while not LoopRestartEvent.is_set():
                await Send({"op": OPCode.HEARTBEAT, "d": LastSequence})
                LoopRestartEvent.wait(HeartbeatInterval)

            LoopRestartEvent.clear()

        LastSequence = None
        HeartbeatThread = threading.Thread(target=asyncio.run, args=(HeartbeatLoop(),))
        HeartbeatThread.start()

        # Send Identify
        identify = {}
        identify["op"] = OPCode.IDENTIFY
        identify["d"] = {}
        identify["d"]["token"] = prod_api_helpers.BotToken
        identify["d"]["intents"] = sum(map(lambda x: 1 << x, Intents))
        identify["d"]["properties"] = {}
        identify["d"]["properties"]["os"] = platform.system().lower()
        identify["d"]["properties"]["browser"] = "DiscordBot"
        identify["d"]["properties"]["device"] = "DiscordBot"

        await Send(identify)

        # Start processing events
        while True:
            current_event = await Receive()

            if prod_config.args.debug:
                pprint(current_event)

            match current_event["op"]:
                case OPCode.DISPATCH:
                    LastSequence = current_event["s"]

                    # Skip if message is from this bot or not from this guild.
                    # Also skip if they have an ignored role
                    if current_event["t"] in ["MESSAGE_CREATE", "MESSAGE_UPDATE"]:
                        is_message_for_this_bot = current_event["d"]["author"]["id"] == prod_api_helpers.SelfID
                        is_message_from_other_guild = current_event["d"]["guild_id"] != prod_api_helpers.GuildId
                        is_message_from_ignored_role = any(map(lambda x: x in prod_api_helpers.IgnoredRoles, current_event["d"]["member"]["roles"]))

                        if any([is_message_for_this_bot, is_message_from_other_guild, is_message_from_ignored_role]):
                            continue

                    # Call all functions that listen to this event
                    if current_event["t"] in EventHooks.keys():
                        for f in EventHooks[current_event["t"]]:
                            f(current_event["d"])

while True:
    try:
        asyncio.run(WebSocketLoop())
    except Exception as e:
        print(e)
        print("Restarting Discord Gateway")
        LoopRestartEvent.set()
        while HeartbeatThread != None and HeartbeatThread.is_alive():
            pass
        sleep(1)