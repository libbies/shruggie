#!/usr/bin/env python3
import discord
import re

from config import *
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
    urls, and delete the entire message if the urls aren't on the whitelist
    also the bot commands are here because why not :("""

    # log all messages
    if message.channel.name is not None:
        logger(message.channel.name).debug('{}#{}: {}'.format(
            message.author.display_name,
            message.author.discriminator,
            message.content,
        ))

    # !repr :3
    if message.channel.name == 'technical-nonsense' and message.content[0:5] == '!repr':
        return await bot.send_message(message.channel, repr(bot))

    # handle admin commands
    if message.channel.name == 'mod-channel'
        # print a list of the bot's commands
        if message.content[0:5] == '!help':
            return await bot.send_message(message.channel,
                'my available commands are: `!help` `!say` `!list` `!add` `!remove`',
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
                return await bot.send_message(message.channel, 'no such channel')
            return await bot.send_message(channel, ' '.join(message.content.split()[2:]))

        # any bot command below this line is only accessible by server administrators
        if not message.author.server_permissions.administrator:
            return

        # whitelist functions are below here
        # TODO: split bot commands into their own functions, and call them instead
        success = False
        if message.content[0:4] == '!add':
            for substr in message.content.split():
                if re.search('^[a-z]+[.][a-z]+$', substr):
                    whitelist.append(substr)
                    success = True
            else:
                if not success:
                    return await bot.send_message(message.channel,
                        'please specify a domain to add, i.e.: `!add example.com`'
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
                        'please specify a domain to remove, i.e.: `!remove example.com`'
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
                        mod_channel = discord.utils.get(message.server.channels,
                            name='mod-channel',
                            type=discord.ChannelType.text,
                        )
                        return await bot.send_message(mod_channel,
                            'deleted message from {}: ```{} {}#{}: {}```'.format(
                                message.author.mention,
                                message.timestamp.strftime('[%I:%M %p]'),
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
    logger('debug').exception('exception:')
