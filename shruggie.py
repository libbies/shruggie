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
    'wikipedia.org',
    'cnn.com',
    'nytimes.com',
    'washingtonpost.com',
]

@bot.event
async def on_message_edit(bmessage, message):
    """log edited messages"""
    log(message.channel.name, '{}#{}: {} (edited)'.format(
        message.author.name,
        message.author.discriminator,
        message.content,
    ))

@bot.event
async def on_message_delete(message):
    """log deleted messages"""
    log(message.channel.name, '{}#{}: {} (deleted)'.format(
        message.author.name,
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
            message.author.name,
            message.author.discriminator,
            message.content,
        ))

    # !repr - just a diagnostic function, so i can look inside things
    if (message.channel.name == 'technical-nonsense' and
        message.content[0:5] == '!repr'):
        # TODO: parse arguments directly from the message
        return await bot.send_message(message.channel,
            repr(message.server.get_member(message.content.split()[1][3:-1]))
        )

    # handle admin/mod commands
    if message.channel.name == 'mod-channel':
        return await admin_command(message)

    # filter urls that are not on the whitelist
    # default role is the implicit 'everyone'; only one role means non-member
    if (len(message.author.roles) == 1 or
        discord.utils.get(message.author.roles, name=SHRUGGIE_KID_ROLE)):
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
                        log(message.channel.name, '{}#{}: {} (filtered)'.format(
                            message.author.name,
                            message.author.discriminator,
                            repr(message.content),
                        ))
                        await bot.delete_message(message)
                        channel = discord.utils.get(message.server.channels,
                            name='mod-channel',
                            type=discord.ChannelType.text,
                        )
                        return await bot.send_message(channel,
                            'filtered message from {} in {}: ```{}#{}: {}```'.format(
                                message.author.mention,
                                message.channel.mention,
                                message.author.name,
                                message.author.discriminator,
                                message.content,
                            ))

async def admin_command(message):
    # we can probably break all of these into their own individual functions
    # probably in a seperate .py file, maybe?
    cmd = message.content.split()[0]
    if cmd[0] == SHRUGGIE_CMD_PREFIX:
        cmd = cmd[1:]
        # print a list of the bot's commands
        if cmd == 'help':
            return await bot.send_message(message.channel,
                'my available commands are: `!say` `!timeout` `!list` `!add` `!remove`',
            )

        # put a user into timeout
        if cmd == 'timeout':
            user = message.content.split()[1]
            if user[0:2] == '<@' and user[-1] == '>':
                user = message.server.get_member(user[2:-1])
            else:
                user = discord.utils.get(message.server.members, name=user)
            role = discord.utils.get(message.server.roles, name='timeout')
            return await bot.add_roles(user, role) 

        # put a user into timeout
        if cmd == 'untimeout':
            user = message.content.split()[1]
            if user[0:2] == '<@' and user[-1] == '>':
                user = message.server.get_member(user[2:-1])
            else:
                user = discord.utils.get(message.server.members, name=user)
            role = discord.utils.get(message.server.roles, name='timeout')
            return await bot.remove_roles(user, role) 

        # have the bot say something in another channel:
        if cmd == 'say':
            channel = message.content.split()[1]
            if channel[0:2] == '<#' and channel[-1] == '>':
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

        # success used to track if add/remove items to whitelist worked or not
        success = False
        # add item to whitelist
        if cmd == 'add':
            for substr in message.content.split():
                if re.search('^[a-z]+[.][a-z]+$', substr):
                    whitelist.append(substr)
                    success = True
            else:
                if not success:
                    return await bot.send_message(message.channel,
                        'specify domain(s) to add: `!add example.com`'
                    )

        # remove item from whitelist
        if cmd == 'remove':
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

        # print the whitelist, or, if add/remote worked, print the whitelist
        if cmd == 'list' or success:
            return await bot.send_message(message.channel,
                'whitelist contains: ```{}```'.format(repr(whitelist))
            )

@bot.event
async def on_ready():
    # TODO: code to set/save the current nickname
    debug('login: {}#{}'.format(bot.user.name, bot.user.discriminator))
    for server in bot.servers:
        if server.get_member(bot.user.id).display_name != SHRUGGIE_NICKNAME:
            await bot.change_nickname(server.get_member(bot.user.id),
                SHRUGGIE_NICKNAME,
            )

try:
    bot.run(SHRUGGIE_APP_TOKEN)
except:
    logger(None).exception('exception:')
