from importlib import reload ## DEBUGGING
import const
from private_info import API_TOKEN, BOT_ID, LOG_PATH
import discord
import runner
import logging
import random
import classes.Game as GameManager

logging.basicConfig(filename=f'{LOG_PATH}/quidditchbot.log', filemode='a',level=logging.INFO,format='%(asctime)s - %(message)s')
client = discord.Client()
GM = None # Aren't global variables fun?!

l = logging.info # Me being lazy.

######################
##   TODO   ##
######################
#   - Quidditch commands

favorite_user = None
flagged_message = 0
CHANNEL = ['the-field'] # Channels that QuidditchBot is not allowed in at all.

@client.event
async def on_ready():
	l('We have logged in as {0.user}'.format(client))
	await set_status()
	# For now, we're going to hard-code the players....
	players = []
	player1 = {	'name':"Bijan",
				'discordID':318849064307523584,
				'charID':1,
				'jersey':0,
				'house':"Ravenclaw",
				'role':"chaser"}
	players.append(player1)
	global GM
	print("Initializing Game Manager...")
	GM = GameManager.Game(players)




'''
All commands to this bot must be prefixed with an emoji.
That emoji is checked against the current teams playing to make sure it's valid
If it is, that action is sent to the game manager (GM) to figure out what to do with it
Wait for a response from the GM, and decide what to do from there.
'''
@client.event
async def on_message(message):
	# If it's ourselves, ignore it
	if message.author.bot:
		return

	# Is this a DM?
	if str(message.channel.type) == 'private':
		return # ignore for now.

	# We only care about messages in specific channels
	if str(message.channel) not in CHANNEL:
		return

	if message.content.startswith('reload'):
		reloadCommands()
		return await message.channel.send("Gotcha boss! 👍")

	if message.content.startswith('die'):
		exit()

	if message.content.startswith(const.EMOJI_PREFIXES):
		# It's an emoji, but is it the correct emoji?
		#TODO: validate the houses.
		global GM
		return await runner.newAction(message, GM)

	#Finally, if none of the above conditions are met, just delete the message.
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
async def set_status():
	new_status = random.choice(const.STATUS_LIST).split(': ')
	activity = discord.Activity(name=new_status[1],type=const.ACTION_ENUM[new_status[0]])
	l(f"New Activity: {new_status}")
	await client.change_presence(activity=activity)

# Hot-reloading libs - FOR DEBUGGING ONLY 
def reloadCommands():
	reload(runner)
	runner.reloadLibs()
	return


client.run(API_TOKEN)