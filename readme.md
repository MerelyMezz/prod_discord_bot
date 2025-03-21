# Prod Discord Bot

This is a simple discord moderation bot that will quarantine users who do any of the following:
- Posting markdown links, that obscure the destination of a URL
- Using @everyone and @here mentions in a post
- Creating posts in multiple channels rapidly

This bot will only work for one server per process.
## Configuration

The default configuration file is `prod.conf` in the current working directory. The path of the config file can be changed with the `--config [filepath]` parameter. In addition to the main config file, drop-in config files in the directory `[config file path].d` will be appended.

The config file should look like this:

```
BotToken [Paste bot token from discord]
Guild [paste guild id]

LogChannel [paste channel id where logs should be posted]
QuarantineRole [paste role id that offending accounts should be assigned]

IgnoreRole [role to be ignored by the bot, such as staff] True

EnableModule block_markdown_links True
EnableModule block_at_everyone True
EnableModule block_multi_channel_spam True

MultiChannelSpamIntervalSeconds 10
MultiChannelSpamPostCountThreshold 3
```
## Modules

Modules are python code files, that will dynamically be loaded when placed in the `modules` folder and enabled in the config with `EnableModule [filename without extension] True`. You can write your own modules and have your functions be called, by declaring them in a dictionary called `ModuleFunctions`. The keys are Discord's Gateway Event names and the values are sets of function names in the local module to call. The function will be passed the event data (the "d" field of a Gateway Event Payload).

Some helper functions are also provided:

### `Api_Request(request_type, api_string, body=None)`
A generic function to call API functions that don't have their own helper functions yet.
- `request_type`: The kind of HTTP request to use. Can be `get`,`post`,`put` or `delete`
- `api_string`: The API request url. Only the actual command itself goes here, i.e. `/channels/1234` to get the channel with the id `1234`.
- `body`: The body of a `post` or `put` request goes here. Should usually contain a JSON string.
### `PostMessage(channel_id, message)`
Posts a simple text message in a channel.
- `channel_id`: The id of the channel the message will appear in.
- `message`: the plain text contents of the message.
### `PostLogMessage(message)`
Posts a text message in the log channel, useful to keep track of any actions the bot has performed.
- `message`: The message that will appear in the logs.
### `DeleteMessage(message_data):`
Deletes a message and leaves a message in the logs, preserving the contents of the deleted message and its author
- `message_data`: The entire message object of the message to be deleted.
### `QuarantineUser(user_id, reason):`
Assigns the quarantine role to a user, which if set up correctly on the server, will prevent them from posting in any publicly accessible channels. Users can then be banned by human staff or de-quarantined, if it turned out they were mistakenly quarantined.
- `user_id`: The ID of the user to be assigned quarantine.
- `reason`: The reason for the quarantine.
