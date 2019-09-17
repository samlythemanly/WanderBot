from importlib import reload ## DEBUGGING
import const
from private_info import API_TOKEN, BOT_ID
import discord
import commands
import logging
import random

logging.basicConfig(level=logging.INFO)
client = discord.Client()

######################
##       TODO       ##
######################
#    - LOGGING
#    - DB engine
#    - Quidditch commands
#    - Upload File via DM
#    - Help on individual commands
#    - More easter eggs?
#    - fuckin everything else

favorite_user = None

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await change_status()

@client.event
async def on_message(message):
    # If it's ourselves, ignore it
    if message.author == client.user:
        return

    # Is this a DM?
    if message.channel.type == 'private':
        return # ignore for now.

    # We only care about messages in specific channels
    if str(message.channel) not in const.ALLOWED_CHANNELS:
        return

    # So there's a message in a text channel that we care about.
    # Let's see if someone is trying to talk to the bot
    if message.content.startswith(const.TRIGGER_SYMBOL):
        # Yep. What the fuck do they want.
        return await parseMessage(message)

       # Let's get the easter eggs out of the way...
       # We only do this if they're not trying to write a command.
    else:
        if 'wanderbot' in message.content.lower():
            await message.add_reaction('👋')
        if 'drama' in message.content.lower():
            await message.add_reaction('👀')
        if 'good bot' in message.content.lower():
            await message.add_reaction('😊')
        if 'bad bot' in message.content.lower():
            await message.add_reaction(':cold_sweat:')
        if message.mentions:
            for mention in message.mentions:
                if mention.id == BOT_ID: # our own ID
                    await message.add_reaction('👋')

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == client.user: #They reacted to us!
        global favorite_user
        favorite_user = user
        print(user)
        print(user.name)
        return

async def parseMessage(message):
    prefix = message.content.split(' ')[0][1:].lower() #Get the first word of the message without the symbol
    # Verify it's a valid command
    if prefix in commands.COMMANDS:
        # Make sure the user has permissions
        if not checkUserRole(prefix,message.author):
            return await message.channel.send(f"I'm sorry {message.author.mention}, you can't do that")
        # Handle the 'special' commands
        if prefix == 'reload':
            reloadCommands()
            return await message.channel.send("Gotcha boss! 👍")
        if prefix == 'change_status':
            return await change_status()
        # Okay, pass control to the commands module.
        return await commands.runner(prefix,message)
    else:
        return await message.channel.send(f"Whoops! Never heard of that command, {message.author.name}. Try again?")

def checkUserRole(command, author):
    if 'Robot' in [str(r) for r in author.roles]:
        return True
    if commands.COMMANDS[command]['roles'][0] == 'all':
        return True
    else:
        for role in commands.COMMANDS[command]['roles']:
            if role in [str(r) for r in author.roles]:
                return True
    return False

# Change the bot's activity
#   Cycle to the next random activity the bot can do
async def change_status():
    new_status = random.choice(const.STATUS_LIST).split(': ')
    activity = discord.Activity(name=new_status[1],type=const.ACTION_ENUM[new_status[0]])
    print(f"New Activity: {new_status}")
    await client.change_presence(activity=activity)

# Hot-reloading libs - FOR DEBUGGING ONLY 
def reloadCommands():
    reload(commands)
    commands.reloadLibs()
    return


client.run(API_TOKEN)