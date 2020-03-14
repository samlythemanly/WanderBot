import os
from importlib import reload  ## DEBUGGING

import discord
import logging
import random

from wanderbot.Quidditch.runner import reloadLibs, loadRoster, createScoreboard, newAction
from wanderbot.Quidditch.classes import Game as GameManager

from wanderbot.Quidditch.const import STATUS_LIST, ROLES, EMOJI_PREFIXES, ACTION_ENUM


from pathlib import Path  # python3 only
from dotenv import load_dotenv

env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

logging.basicConfig(filename=f'{os.getenv("LOG_PATH")}/quidditchbot.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s - %(message)s')
client = discord.Client()
GM = None  # Aren't global variables fun?!

l = logging.info  # Me being lazy.

######################
##   TODO   ##
######################
#   - Quidditch commands
#  - Better log statements for what's going on (convert all prints to logs)
#  - Logging on deleted statements?

favorite_user = None
flagged_message = 0
GAME_CHANNEL = 'the-field'  # Where the game will take place
ADMIN_CHANNEL = "announcers-booth"  # Allows Admins to interact with the bot (load players, end turn, etc...)
ALLOWED_CHANNELS = [GAME_CHANNEL, ADMIN_CHANNEL]


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await set_status()
    # For now, we're going to hard-code the players....
    # players = []
    # player1 = {  'name':"Bijan",
    #       'charID':1,
    #       'house':"Ravenclaw",
    #       'role':"chaser"}
    #       'jersey':0,
    #       'discordID':318849064307523584,
    # players.append(player1)
    global GM
    print("Initializing Game Manager...")
    # Game manager Init. Set up players, custom objects, etc...
    # TODO: Save inital state to DB. Or local file?
    GM = GameManager.Game()


'''
All commands to this bot must be prefixed with an emoji.
That emoji is checked against the current teams playing to make sure it's valid
If it is, that action is sent to the game manager (GM) to figure out what to do with it
Wait for a response from the GM, and decide what to do from there.
'''


@client.event
async def on_message(message):
    global GM
    # If it's ourselves, ignore it
    if message.author.bot:
        return

    # Is this a DM?
    if str(message.channel.type) == 'private':
        return  # ignore for now.

    # We only care about messages in specific channels
    if str(message.channel) not in ALLOWED_CHANNELS:
        return

    ### DEBUGGING
    if message.content.startswith('reload'):
        reloadCommands()
        return await message.channel.send("Gotcha boss! 👍")
    if message.content.startswith('die'):
        print("Dying!")
        exit()
    ###END DEBUGGING

    if str(message.channel) == ADMIN_CHANNEL:
        # Admin channel to load players
        if message.content.startswith('!roster'):
            with message.channel.typing():
                await message.channel.send("Initializing QuidditchBot!")

                purge_message = await message.channel.send("Purging all messages in `#the-field`...")
                await purgeTheField(message)
                await purge_message.edit(content=purge_message.content + " Done!")

                create_player_message = await message.channel.send("Loading players, this may take a minute...")
                res = await loadRoster(message, GM)
                if not res:
                    return
                await create_player_message.edit(content=create_player_message.content + " Done!")

                scoreboard_message = await message.channel.send("Creating scoreboard and pinning it...")
                await createScoreboard(message, GAME_CHANNEL)
                await scoreboard_message.edit(content=scoreboard_message.content + " Done!")

                return await message.channel.send("---------------\nSuccessfully loaded QuidditchBot. Ready to play!!")
        else:
            return

    if message.content.startswith(EMOJI_PREFIXES):
        # It's an emoji, but is it the correct emoji?
        # TODO: validate the houses.
        print(f"New message: {message.content}")
        return await newAction(message, GM)

    # Finally, if none of the above conditions are met, just delete the message.
    return await message.delete()


def authorizeCommand(command, message):
    # Dev role gets auto-approved
    if 'Robot' in [str(r) for r in message.author.roles]:
        return True
    # Check the user's role for this command.
    if commands.COMMANDS[command]['roles'][0] == ROLES.ALL:
        return True
    else:
        for role in commands.COMMANDS[command]['roles']:
            if role in [str(r) for r in message.author.roles]:
                l(f"Matched on user's role: {role}.")
                return True
    return False


# Change the bot's activity
#   Cycle to the next random activity the bot can do
async def set_status():
    new_status = random.choice(STATUS_LIST).split(': ')
    activity = discord.Activity(name=new_status[1], type=ACTION_ENUM[new_status[0]])
    l(f"New Activity: {new_status}")
    await client.change_presence(activity=activity)


# This function will delete ALL messages in GAME_CHANNEL so we can start anew.
async def purgeTheField(message):
    for ch in message.guild.channels:
        if str(ch) == GAME_CHANNEL:
            print(f"Deleting all messages in #{ch}")
            deleted_messages = await ch.purge(limit=1000)
            print(f"Deleted {len(deleted_messages)} messages!")


# Hot-reloading libs - FOR DEBUGGING ONLY
def reloadCommands():
    runner_modules = [reloadLibs, loadRoster, createScoreboard, newAction]
    for modules in runner_modules:
        reload(modules)
    reloadLibs()
    return



client.run(os.getenv("API_TOKEN"))
