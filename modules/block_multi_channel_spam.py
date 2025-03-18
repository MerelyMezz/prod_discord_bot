import prod_api_helpers
import prod_config
import datetime
from itertools import chain

ModuleFunctions = {}
ModuleFunctions["MESSAGE_CREATE"] = {"TrackMultiChannelPostingFrequency"}

MultiChannelSpamIntervalSeconds = prod_config.GetConfigFloat("MultiChannelSpamIntervalSeconds")
MultiChannelSpamPostCountThreshold = prod_config.GetConfigFloat("MultiChannelSpamPostCountThreshold")

PostsPerChannelPerUser = {}

def TrackMultiChannelPostingFrequency(d):
    # Insert new post into dictionary
    user_id = d["author"]["id"]
    if not user_id in PostsPerChannelPerUser.keys():
        PostsPerChannelPerUser[user_id] = {}

    channel_id = d["channel_id"]
    if not channel_id in PostsPerChannelPerUser[user_id].keys():
        PostsPerChannelPerUser[user_id][channel_id] = []

    current_time = datetime.datetime.fromisoformat(d["timestamp"])
    d["timestamp_datetime"] = current_time
    PostsPerChannelPerUser[user_id][channel_id] += [d]

    # Clear out any posts that are too old to be counted
    channel_lists_to_delete = []
    for channel_id in PostsPerChannelPerUser[user_id].keys():
        PostsPerChannelPerUser[user_id][channel_id] = list(filter(lambda x: (current_time - x["timestamp_datetime"]).total_seconds() < MultiChannelSpamIntervalSeconds, PostsPerChannelPerUser[user_id][channel_id]))
        if len(PostsPerChannelPerUser[user_id][channel_id]) == 0:
            channel_lists_to_delete += [channel_id]

    for channel_id in channel_lists_to_delete:
        del PostsPerChannelPerUser[user_id][channel_id]

    # Check if channel threshold has been reached
    if len(PostsPerChannelPerUser[user_id]) < MultiChannelSpamPostCountThreshold:
        return

    # Ban offending user
    prod_api_helpers.QuarantineUser(d["author"]["id"], "Posted too quickly in too many channels")
    for message in chain(*PostsPerChannelPerUser[user_id].values()):
        prod_api_helpers.DeleteMessage(message)