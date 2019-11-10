from importlib import reload ## DEBUGGING
import const
from private_info import API_TOKEN, TEST_TOKEN, BOT_ID, LOG_PATH
import discord
import commands, audit
import logging
import random
import sys

if len(sys.argv) < 2:
    print("Usage: python bot.py <PROD|DEV>")
    exit(-1)
if sys.argv[1] == 'DEV':
    logging.basicConfig(filename=f'{LOG_PATH}/testbot.log', filemode='a',level=logging.INFO,format='%(asctime)s - %(message)s')
    TOKEN = TEST_TOKEN
elif sys.argv[1] == 'PROD':
    logging.basicConfig(filename=f'{LOG_PATH}/wanderbot.log', filemode='a',level=logging.INFO,format='%(asctime)s - %(message)s')
    TOKEN = API_TOKEN
else:
    print("Usage: python bot.py <PROD|DEV>")
    exit(-1)

client = discord.Client()

l = logging.info # Me being lazy.

######################
##       TODO       ##
######################
#    - DB engine
#    - Help with individual commands
#    - Fuzzy command helper?
#    - More easter eggs?
#    - Gambling?

favorite_user = None
flagged_message = 0
CHANNEL_BLACKLIST = ['the-lobby'] # Channels that WanderBot is not allowed in at all.

@client.event
async def on_ready():
    l('We have logged in as {0.user}'.format(client))
    await change_status()

@client.event
async def on_message(message):
    # If it's ourselves, ignore it
    if message.author == client.user:
        return

    # Is this a DM?
    if str(message.channel.type) == 'private':
        l(f"\n-------------\nNew DM from {message.author}:")
        l(message.content)
        return # ignore for now.

    # We only care about messages in specific channels
    if str(message.channel) in CHANNEL_BLACKLIST:
        return

    # So there's a message in a text channel that we care about.
    # Let's see if someone is trying to talk to the bot
    if message.content.startswith(const.TRIGGER_SYMBOL):
        # Yep. What the fuck do they want.
        return await parseMessage(message)

       # Let's get the easter eggs out of the way...
       # We only do this if they're not trying to write a command.
    else:
        if 'bad wanderbot' in message.content.lower():
            return await message.add_reaction('😢')
        if 'wanderbot' in message.content.lower():
            await message.add_reaction('👋')
        if 'drama' in message.content.lower():
            await message.add_reaction('👀')
        if 'good bot' in message.content.lower():
            await message.add_reaction('😊')
        if 'bad bot' in message.content.lower():
            await message.add_reaction('😢')
        if 'spooky' in message.content.lower():
            await message.add_reaction('👻')
        if message.mentions:
            for mention in message.mentions:
                if mention.id == BOT_ID: # our own ID
                    await message.add_reaction('👋')

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == client.user: #They reacted to us!
        global favorite_user
        favorite_user = user
        return

# @client.event
# async def on_message_delete(message):
#     return await audit.logDeletedMessage(message,discord.AuditLogAction.message_delete)
    # if a message was deleted, we should search the audit logs for it?
    # Audit event: message_delete
    # async for entry in guild.audit_logs(action=discord.AuditLogAction.message_delete):
    #   print('{0.user} banned {0.target}'.format(entry))

    # If a message gets deleted, we want to know who deleted it and what was the original message.
    # If the message was deleted by someone other than the original author we need to look at the internal audit logs
    # async for entry in message.guild.audit_logs(action=discord.AuditLogAction.message_delete):
    #     print(entry.target)
        # if entry.target.id == message.id:
        #     print("found message")
        #     return await message.channel.send(f"{target.user.name} just deleted the following message from {message.author.name}: {message.content}")


# @client.event
# async def on_message_edit(message_before, message_after):
#     return await message.channel.send(f"{message.author.name} just edited their message from: `{message_before.content}` to: `{message_after.content}`")


async def parseMessage(message):
    prefix = message.content.split(' ')[0][1:].lower() #Get the first word of the message without the symbol
    l(f"\n-------------\nCommand from: {message.author} in channel '{str(message.channel)}' - '{prefix}'")
    # Verify it's a valid command
    if prefix in commands.COMMANDS:
        # First, make sure this command can be run in the current channel. If not, fail silently.
        ch_flag = False
        for ch in commands.COMMANDS[prefix]['channels']:
            if str(message.channel) == ch:
                ch_flag = True
                break
        if not ch_flag:
            l(f"Channel '{str(message.channel)}' does not allow that command.")
            return await message.channel.send(f"I'm sorry {message.author.mention}, I can't do that in this channel :( But I can give you a hug!")
        # Make sure the user has permissions
        if not authorizeCommand(prefix,message):
            l(f"User {message.author} does not have permissions to run that command")
            return await message.channel.send(f"I'm sorry {message.author.mention}, you can't do that! It's not me, it's you.")
        # Handle the 'special' commands
        if prefix == 'reload':
            l(f"Reloading modules")
            reloadCommands()
            return await message.channel.send("Gotcha boss! 👍")
        if prefix == 'change_status':
            l("Changing status")
            return await change_status()
        # Okay, pass control to the commands module.
        l(f"Authorized user {message.author} to run {prefix}. Executing.")
        return await commands.runner(prefix,message)
    else:
        l(f"Could not find '{prefix}' in commands list.")
        return await message.channel.send(f"Whoops! Never heard of that command, {message.author.mention}. Try again?")

def authorizeCommand(command, message):
    # Dev role gets auto-approved
    if 'Robot' in [str(r) for r in message.author.roles]:
        return True
    # Check the user's role for this command.
    if commands.COMMANDS[command]['roles'][0] == const.ROLES.ALL:
        return True
    else:
        for role in commands.COMMANDS[command]['roles']:
            if role in [str(r) for r in message.author.roles]:
                l(f"Matched on user's role: {role}.")
                return True
    return False

# Change the bot's activity
#   Cycle to the next random activity the bot can do
async def change_status():
    new_status = random.choice(const.STATUS_LIST).split(': ')
    activity = discord.Activity(name=new_status[1],type=const.ACTION_ENUM[new_status[0]])
    l(f"New Activity: {new_status}")
    await client.change_presence(activity=activity)

# Hot-reloading libs - FOR DEBUGGING ONLY 
def reloadCommands():
    reload(commands)
    commands.reloadLibs()
    return


client.run(TOKEN)