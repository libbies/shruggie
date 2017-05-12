#!/usr/bin/env python3
import discord
import re

from helpers import logger, debug

bot = discord.Client()

whitelist = [
    'imgur.com',
    'youtube.com',
    'discordapp.com',
    'youtu.be',
    'reddit.com',
    'redd.it',
    'gfycat.com',
    'twitter.com',
]

channels = dict()
async def update_state(server):
    """update internal bot state"""
    for channel in server.channels:
        if not channels.get(server.id + channel.name):
            channels[server.id + channel.name] = channel.id

@bot.event
async def on_message_edit(bmessage, message):
    """log edited messages"""
    logger(message.channel.name).debug('{}#{}: {} (edited)'.format(
        message.author.display_name,
        message.author.discriminator,
        message.content,
    ))

@bot.event
async def on_message_delete(message):
    """log deleted messages"""
    logger(message.channel.name).debug('{}#{}: {} (deleted)'.format(
        message.author.display_name,
        message.author.discriminator,
        message.content,
    ))

@bot.event
async def on_message(message):
    """scan all messages from users without any roles (i.e.: non-members) for
    urls, and delete the entire message if the urls aren't on the whitelist"""

    # log all messages
    if message.channel.name is not None:
        logger(message.channel.name).debug("{}#{}: {}".format(
            message.author.display_name,
            message.author.discriminator,
            message.content,
        ))

    # !repr :3
    if message.channel.name == 'technical-nonsense' and message.content[0:5] == '!repr':
        await update_state(message.server)
        return await bot.send_message(message.channel, repr(channels))

    # handle admin commands
    if message.channel.name == 'mod-channel' and message.author.server_permissions.administrator:
        if message.content[0:4] == '!say':
            await update_state(message.server)
            channel = message.content.split()[1]
            if channel[0:2] == '<#' and channel[-1] == '>':
                channel_id = channel[2:-1]
            else:
                if not channels.get(message.server.id+channel):
                    return await bot.send_message(message.channel, "no such channel")
                channel_id = channels.get(message.server.id+channel)
            return await bot.send_message(message.server.get_channel(channel_id),
                    " ".join(message.content.split()[2:]),
            )

        success = False
        if message.content[0:5] == '!help':
            return await bot.send_message(message.channel,
                "my available commands are: `!list` `!add example.com` `!remove example.com`",
            )
        if message.content[0:4] == '!add':
            for substr in message.content.split():
                if re.search('^[a-z]+[.][a-z]+$', substr):
                    whitelist.append(substr)
                    success = True
            else:
                if not success:
                    return await bot.send_message(message.channel, "sorry, couldn't do that")
        if message.content[0:7] == '!remove':
            for substr in message.content.split():
                if re.search('^[a-z]+[.][a-z]+$', substr):
                    if substr in whitelist:
                        whitelist.remove(substr)
                        success = True
            else:
                if not success:
                    return await bot.send_message(message.channel, "sorry, couldn't do that")
        if success or message.content[0:5] == '!list':
            return await bot.send_message(message.channel,
                "whitelist contains: ```{}```".format(repr(whitelist))
            )

    # default role is the implicit 'everyone'; only one role means non-member
    if len(message.author.roles) == 1:
        if 'http' in message.content:
            for substr in message.content.split():
                if 'http' in substr:
                    for url in whitelist:
                        if re.search('https?://([a-z]+[.])*' + url, substr):
                            # if a whitelisted site is found, exit inner for loop 
                            break
                    else:
                        # if not on the whitelist, delete the message
                        debug('deleted message from {}#{}: {}'.format(
                            message.author.display_name,
                            message.author.discriminator,
                            repr(message.content),
                        ))
                        await bot.delete_message(message)
                        for channel in message.server.channels:
                            if channel.name == 'mod-channel' and channel.type.text:
                                return await bot.send_message(channel,
                                    'deleted message from {}: ```{} {}#{}: {}```'.format(
                                    message.author.mention,
                                    message.timestamp.strftime("[%I:%M %p]"),
                                    message.author.name,
                                    message.author.discriminator,
                                    message.content,
                                ))

@bot.event
async def on_ready():
    debug('login: {}#{}'.format(bot.user.name, bot.user.discriminator))

@bot.event
async def on_server_join(server):
    await update_state(server)

try:
    bot.run('APP BOT USER TOKEN GOES HERE')
except:
    logger('debug').exception("exception:")
