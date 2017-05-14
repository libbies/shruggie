#!/usr/bin/env python3
import discord
import re

from config import *
from helpers import logger, debug, log

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

@bot.event
async def on_message_edit(bmessage, message):
    """log edited messages"""
    log(message.channel.name, '{}#{}: {} (edited)'.format(
        message.author.display_name,
        message.author.discriminator,
        message.content,
    ))

@bot.event
async def on_message_delete(message):
    """log deleted messages"""
    log(message.channel.name, '{}#{}: {} (deleted)'.format(
        message.author.display_name,
        message.author.discriminator,
        message.content,
    ))

@bot.event
async def on_message(message):
    """scan all messages from users without any roles (i.e. non-members)
    for urls, and delete the entire message if the urls aren't on the
    whitelist. also the bot commands are here because why not :("""

    # log all messages
    if message.channel.name is not None:
        log(message.channel.name, '{}#{}: {}'.format(
            message.author.display_name,
            message.author.discriminator,
            message.content,
        ))

    # !repr :3 just a diagnostic function, so i can look inside things
    if (message.channel.name == 'technical-nonsense' and
        message.content[0:5] == '!repr'):
        # TODO: parse arguments, if any
        return await bot.send_message(message.channel, repr(dir(bot)))

    # handle admin commands
    if message.channel.name == 'mod-channel':
        # print a list of the bot's commands
        if message.content[0:5] == '!help':
            return await bot.send_message(message.channel,
                'my available commands are: `!say` `!list` `!add` `!remove`',
            )

        # have the bot say something in another channel:
        if message.content[0:4] == '!say':
            channel = message.content.split()[1]
            if channel[0:2] == '<#' and ch[-1] == '>':
                channel = message.server.get_channel(channel[2:-1])
            else:
                channel = discord.utils.get(message.server.channels,
                    name=channel,
                    type=discord.ChannelType.text
                )
            if not channel:
                return await bot.send_message(message.channel,
                    'no such channel'
                )
            return await bot.send_message(channel,
                ' '.join(message.content.split()[2:])
            )

        # any command below here is only accessible by server admins
        if not message.author.server_permissions.administrator:
            return

        # whitelist functions are below here
        # TODO: split bot commands into their own functions
        #   and wrap them up below or call them directly
        success = False
        if message.content[0:4] == '!add':
            for substr in message.content.split():
                if re.search('^[a-z]+[.][a-z]+$', substr):
                    whitelist.append(substr)
                    success = True
            else:
                if not success:
                    return await bot.send_message(message.channel,
                        'specify domain(s) to add: `!add example.com`'
                    )

        if message.content[0:7] == '!remove':
            for substr in message.content.split():
                if re.search('^[a-z]+[.][a-z]+$', substr):
                    if substr in whitelist:
                        whitelist.remove(substr)
                        success = True
            else:
                if not success:
                    return await bot.send_message(message.channel,
                        'specify domain(s) to remove: `!remove example.com`'
                    )

        if success or message.content[0:5] == '!list':
            return await bot.send_message(message.channel,
                'whitelist contains: ```{}```'.format(repr(whitelist))
            )

    # default role is the implicit 'everyone'; only one role means non-member
    if len(message.author.roles) == 1:
        if 'http' in message.content:
            for substr in message.content.split():
                if 'http' in substr:
                    for url in whitelist:
                        if re.search('https?://([a-z]+[.])*{}'.format(url),
                                substr):
                            # if on the whitelist, break out of inner for loop
                            break
                    else:
                        # if not on the whitelist, delete the message
                        debug('deleted message from {}#{}: {}'.format(
                            message.author.display_name,
                            message.author.discriminator,
                            repr(message.content),
                        ))
                        await bot.delete_message(message)
                        channel = discord.utils.get(message.server.channels,
                            name='mod-channel',
                            type=discord.ChannelType.text,
                        )
                        return await bot.send_message(channel,
                            'deleted message from {}: ```{}#{}: {}```'.format(
                                message.author.mention,
                                message.author.name,
                                message.author.discriminator,
                                message.content,
                            ))

@bot.event
async def on_ready():
    # TODO: code to set/save the current nickname
    debug('login: {}#{}'.format(bot.user.name, bot.user.discriminator))
    for server in bot.servers:
        if server.get_member(bot.user.id).display_name != SHRUGGIE_NICK_NAME:
            await bot.change_nickname(server.get_member(bot.user.id),
                SHRUGGIE_NICK_NAME,
            )

try:
    bot.run(SHRUGGIE_APP_TOKEN)
except:
    logger(None).exception('exception:')
