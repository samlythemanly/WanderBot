from importlib import reload ## DEBUGGING
import asyncio
import const
from private_info import API_TOKEN, TEST_TOKEN, BOT_ID, LOG_PATH
import discord
import commands, audit
import logging
import random
import os, sys, signal, subprocess # Oh yes, we're going to do some super weird stuff.

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
#    - Help with individual commands
#    - Fuzzy command helper?
#    - More easter eggs?

favorite_user = None
flagged_message = 0
CHANNEL_BLACKLIST = ['the-lobby','the-field','announcers-booth'] # Channels that WanderBot is not allowed in at all.
q_proc = None # QuidditchBot PID, if needed


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
        if message.content.startswith(const.TRIGGER_SYMBOL*2): # Sometimes someone will just type a message that is '!!!!' so we ignore those
            return
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

@client.event
async def on_message_delete(message):
    if message.author.bot or str(message.channel) in CHANNEL_BLACKLIST:
        return
    return await getAuditChannel(message).send(f"{'-'*20}\nA message was deleted in `{str(message.channel)}`:\nOriginal Author: `{message.author}`\nMessage: `{message.content}`\n(The original author might not have been the one to delete this message, check Discord's Audit Log for more info)")



# Audit log any edited messages. We're not going to track who deleted messages because the Discord Audit Log already does that.
@client.event
async def on_message_edit(message_before, message_after):
    if message_before.author.bot or str(message.channel) in CHANNEL_BLACKLIST:
        return
    return await getAuditChannel(message_before).send(f"{'-'*20}\n{message_before.author.name} just edited their message in channel: `{str(message_before.channel)}`:\nBefore: `{message_before.content}`\nAfter: `{message_after.content}`")


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
        if prefix.lower() == 'quidditch':
            return await initQuidditchBot(message)
        if prefix.lower() == 'end_quidditch':
            return await teardownQuidditchBot(message)
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

def getAuditChannel(message):
    for ch in message.guild.channels:
            if str(ch) == const.AUDIT_CHANNEL:
                return ch

# Hot-reloading libs - FOR DEBUGGING ONLY 
def reloadCommands():
    reload(commands)
    commands.reloadLibs()
    return

async def initQuidditchBot(message): 
    await message.channel.send(f"Are you sure you want to start QuidditchBot? Respond `yes` or `no`")
    def confirmation(m):
        return m.author == message.author
    try:
        response = await client.wait_for('message', check=confirmation, timeout=5.0)
    except asyncio.TimeoutError:
        return await message.channel.send("Sorry, I didn't get a response in time. Not launching QuidditchBot.")

    if response.content.lower() == 'no':
        return await message.channel.send("Not launching QuidditchBot.")
    if response.content.lower() == 'yes':
        await message.channel.send("Okay! Launching QuidditchBot....")
        # loop = asyncio.ProactorEventLoop()
        # asyncio.set_event_loop(loop)
        # # QuidditchBot is an entirely other python program, so we're going to manage it from here.
        # print(f"{sys.executable} ./Quidditch/quidditch.py")
        # p = await asyncio.create_subprocess_shell(
        #     f"{sys.executable} ./Quidditch/quidditch.py",
        #     stdout=asyncio.subprocess.PIPE,
        #     stderr=asyncio.subprocess.PIPE)
        # stdout, stderr = await p.communicate()
        # if stdout:
        #     print(f'[stdout]\n{stdout.decode()}')
        # if stderr:
        #     print(f'[stderr]\n{stderr.decode()}')
        p = subprocess.Popen([sys.executable, './Quidditch/quidditch.py'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT)
        global q_proc
        q_proc = p.pid
        
async def teardownQuidditchBot(message):
    global q_proc
    if not q_proc:
        return await message.channel.send(f"QuidditchBot is not currently active! You can start it by calling `!quidditch`.")
    await message.channel.send(f"Are you sure you want to end QuidditchBot? *THIS WILL END THE CURRENT GAME, AND DISCARD ALL INFO* Respond `yes` or `no`")
    def confirmation(m):
        return m.author == message.author
    try:
        response = await client.wait_for('message', check=confirmation, timeout=5.0)
    except asyncio.TimeoutError:
        return await message.channel.send("Sorry, I didn't get a response in time. Not ending QuidditchBot.")

    if response.content.lower() == 'no':
        return await message.channel.send("Not ending QuidditchBot.")
    if response.content.lower() == 'yes':
        await message.channel.send("Good game!!! Ending QuidditchBot....")
        os.kill(q_proc,signal.SIGTERM)



client.run(TOKEN)