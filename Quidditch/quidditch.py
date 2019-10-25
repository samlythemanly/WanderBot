from importlib import reload ## DEBUGGING
import const
from private_info import API_TOKEN, BOT_ID, LOG_PATH
import discord
# import commands
import logging
import random

logging.basicConfig(filename=f'{LOG_PATH}/quidditchbot.log', filemode='a',level=logging.INFO,format='%(asctime)s - %(message)s')
client = discord.Client()

l = logging.info # Me being lazy.

######################
##       TODO       ##
######################
#    - Quidditch commands

favorite_user = None
flagged_message = 0
CHANNEL_BLACKLIST = ['the-lobby'] # Channels that QuidditchBot is not allowed in at all.

@client.event
async def on_ready():
    l('We have logged in as {0.user}'.format(client))
    await change_status()

@client.event
async def on_message(message):
    # If it's ourselves, ignore it
    if message.author.bot:
        return

    # Is this a DM?
    if str(message.channel.type) == 'private':
        l(f"\n-------------\nNew DM from {message.author}:")
        l(message.content)
        return # ignore for now.

    # We only care about messages in specific channels
    # if str(message.channel) in CHANNEL_BLACKLIST:
    #     return
    if not str(message.channel) == 'bot-test':
        return

    # So there's a message in a text channel that we care about.
    # Let's see if someone is trying to talk to the bot
    if message.content.startswith(const.TRIGGER_SYMBOL):
        # Yep. What the fuck do they want.
        return await parseMessage(message)


@client.event
async def on_reaction_add(reaction, user):
    pass

async def parseMessage(message):
    if 'ping' in message.content.lower():
        return await message.channel.send('Pong!')
    if 'delete' in message.content.lower():
        return await message.delete()
    

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


client.run(API_TOKEN)