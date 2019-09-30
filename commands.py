from importlib import reload ## DEBUGGING
import random
import db
import const
import logging
import asyncio

l = logging.info

PRODUCTION_CHANNELS = [
	'general',
	'eyebrow-waggling-stuff',
	'pics-and-gif-spam',
	'meme-central',
	'sick-music-bruh',
	'video-killed-the-radio-star',
	'bot-test',
	'feature-requests',
	'bugz',
	'char-dev',
	'iso',
	'gushers',
	'staff-has-fun-sometimes'
	]
TEST_CHANNELS = ['bot-test','feature-requests','temp']
SECRET_CHANNEL = ['temp']
QUIDDITCH = ['the-field']

ROLES=const.ROLES

COMMANDS = {
	# General Commands for everyone	
		'help': {
				'roles':[ROLES.ALL],
				'channels':PRODUCTION_CHANNELS,
				'hidden':False
				},
		'ping': {
				'roles':[ROLES.ALL],
				'channels':PRODUCTION_CHANNELS,
				'hidden':False
				},
		'coin': {
				'roles':[ROLES.ALL],
				'channels':PRODUCTION_CHANNELS,
				'hidden':False
				},
	   	'mock': {
	   			'roles':[ROLES.ALL],
	   			'channels':PRODUCTION_CHANNELS,
	   			'hidden':True
	   			},
	   	'compliment': {
	   			'roles':[ROLES.ALL],
	   			'channels':PRODUCTION_CHANNELS,
	   			'hidden':True
	   			},
	   	'convert': {
	   			'roles':[ROLES.ALL],
	   			'channels': PRODUCTION_CHANNELS,
	   			'hidden':False
	   			},
	   	'joke': {
	   			'roles':[ROLES.ALL],
	   			'channels': PRODUCTION_CHANNELS,
	   			'hidden':True
	   			},
	   	'halp': {
	   			'roles':[ROLES.ALL],
	   			'channels': PRODUCTION_CHANNELS,
	   			'hidden':True
	   			},
	# Admin / Mod commands 
	   	'change_status':{
				'roles':[ROLES.ADMIN,ROLES.MOD],
				'channels':PRODUCTION_CHANNELS,
				'hidden':False
				},
		# 'activity': {
	 #   			'roles':[ROLES.ADMIN],
	 #   			'channels':PRODUCTION_CHANNELS,
	 #   			'hidden':False
	 #   			},
	# Dev commands / in development commands
		'favorite': {
	   			'roles':[ROLES.DEV],
	   			'channels':TEST_CHANNELS,
	   			'hidden':True
	   			},
	   	'link': {
	   			'roles':[ROLES.DEV],
	   			# 'roles':[ADMIN_ROLE,MOD_ROLE],
	   			'channels':TEST_CHANNELS,
	   			'hidden':False
	   			},
	   	'find': {
	   			'roles':[ROLES.DEV],
	   			# 'roles':[ADMIN_ROLE,MOD_ROLE],
	   			'channels':TEST_CHANNELS,
	   			'hidden':False
	   			},
	   	'reload': {
				'roles':[ROLES.DEV],
				'channels':TEST_CHANNELS,
				'hidden':True
				},
}


# Help Command 
#	Lists all the commands the user is allowed to run
async def help(message):
	l("Running 'help'")
	# Get the user roles
	allowed_commands = []
	for command in COMMANDS:
		if COMMANDS[command]['hidden']:
			continue;
		if COMMANDS[command]['roles'][0] == 'all':
			allowed_commands.append(command)
		else:
			for role in COMMANDS[command]['roles']:
				if role in [str(r) for r in message.author.roles]:
					allowed_commands.append(command)
	return await message.channel.send(f"Hi {message.author.mention}, you can run the following commands: {', '.join([f'`{x}`' for x in allowed_commands])}. Remember to add a '!' before the command you want :)")

# Halp Command 
#	Lists all the hidden commands the user is allowed to run
async def halp(message):
	l("Running 'halp'")
	# Get the user roles
	allowed_commands = []
	for command in COMMANDS:
		if COMMANDS[command]['hidden']:
			if COMMANDS[command]['roles'][0] == 'all':
				allowed_commands.append(command)
			else:
				for role in COMMANDS[command]['roles']:
					if role in [str(r) for r in message.author.roles]:
						allowed_commands.append(command)
	return await message.channel.send(f"Surprise {message.author.mention}! You can run the following _*SPECIAL*_ commands: {', '.join([f'`{x}`' for x in allowed_commands])}. Remember to add a '!' before the command you want :)")


# Ping Pong
#	Simply reply 'Pong!' to the users message. Mostly used to check if the bot is up.
async def ping(message):
	l("Running 'pong'")
	return await message.channel.send('Pong!')

# Coin Toss
#	Flips a 'psudo-fair' coin
async def coin(message):
	l("Running 'coin'")
	if random.randint(0,1):
		await message.channel.send('Heads!')
	else:
		await message.channel.send('Tails!')

# Favorite User
#	 Returns the user who last reacted to WanderBot.
# TODO: Fix this
async def favorite(message,current_favorite_user):
	l("Running 'favorite'")
	if current_favorite_user:
		return await message.channel.send(f"{current_favorite_user.display_name} is my current favorite person!")
	else:
		return await message.channel.send(f"I don't have a current favorite person right now!")

# Link User to Character
#	First argument is the discordID (int), all other arguments are comma delimeted characterIDs
#	ex: !link 12345456 24, 25, 26
async def link(message):
	l("Running 'link'")
	parts = message.content.split(' ') #split on space first
	prefix = parts[0] # The original command. Ignore it
	discordID = parts[1] # The id of the person to link to.
	# First, validate the ID and get the user.
	target = await getUserFromID(message,discordID)
	if not target:
		# Invalid discordID, abort.
		return await message.channel.send(f"Sorry, I can't find anyone with that name, try again?")
	charList = ' '.join(parts[2:]).replace(' ','').split(',')
	rows_updated = await db.linkDiscordToCharacters(target.id,charList)
	if rows_updated > 0:
		# We updated some rows, let's see what they are.
		updated_chars = await db.getCharactersFromIDs(charList)
		if updated_chars:
			print(f"Updated Chars: {updated_chars}")
			response = f"Linked {target.display_name} to the following character(s):"
			for c in updated_chars:
				response += f"\n- {c}"
		return await message.channel.send(response)
	else:
		return await message.channel.send(f"Uh-oh. Something went wrong trying to link. Double-check the command and try again?")


# Find Character
#	Searches the db for a character and returns info about them
async def find(message):
	l("Running 'find'")
	parts = message.content.split(' ') #split on space first
	prefix = parts[0]
	charID = parts[1]
	charInfo = await db.getCharacterFromID(charID)
	print(charInfo['ID'])

# Activity Check
#	Takes a user/character and returns the status of that character, as well as post quotas.
#	This command can take numerous forms: ...TODO
# async def activity(message):

# Mock the last tagged user's message
#	Pretty self explanitory
async def mock(message):
	l("Running 'mock'")
	try:
		user_to_mock = message.mentions[0]
	except IndexError:
		return await message.channel.send(f"There's no one tagged to mock! Looks like the only fool here is you, {message.author.mention}!")
	if not user_to_mock:
		return
	if user_to_mock.id == 617172295902822415 and random.choice(range(15)) == 10:
		return await message.channel.send(f"WANDERBOT IS TOO POWERFUL TO BE MOCKED, MORTAL.")

	async for m in message.channel.history():
		if m.author == user_to_mock:
			response = ''
			flag = random.randint(0,1)
			for char in m.content:
				if flag:
					response += char.lower()
					flag = 0
				else:
					response += char.upper()
					flag = 1
			return await message.channel.send(f'"{response}" - {m.author.mention}')

# Compliment the tagged user.
async def compliment(message):
	l("Running 'compliment'")
	try:
		user_to_compliment = message.mentions[0]
	except IndexError:
		return await message.channel.send(f"I don't know who you want me to compliment, so I'll compliment myself. I'm a good bot and I do good things. Thanks {message.author.mention}!")
	compliment = random.choice(const.COMPLIMENTS)
	return await message.channel.send(f"Hey {user_to_compliment.mention}, {compliment}")

# Convert currencies
#	If 1 argument is given, convert from usd/gbp to wizard
#	If 3 arguments are given, convert to usd/gbp
#	Else, return a helpful message
async def convert(message):
	l("Running 'convert'")
	parts = message.content.replace('$','').replace('£','').split(' ')
	args = len(parts[1:])
	# Which direction are they trying to convert?
	if args == 1: # they're trying to convert muggle -> wizard
		#This is going to get ugly. 
		base = float(parts[1])
		gal_usd = round(base/25)
		gal_gbp = round(base/20.05)
		t_usd = base%25
		t_gbp = base%20.05
		sic_usd = round(t_usd/1.47)
		sic_gbp = round(t_gbp/1.18)
		t_usd = t_usd%1.47
		t_gbp = t_gbp%1.18
		knut_usd = round(t_usd/0.05)
		knut_gbp = round(t_gbp/0.04)
		return await message.channel.send(f"{message.author.mention}, ${base:.2f} is roughly equal to {gal_usd} galleons, {sic_usd} sickles, and {knut_usd} knuts.\nBut if you're from across the pond, then £{base:.2f} is roughly equal to {gal_gbp} galleons, {sic_gbp} sickles, and {knut_gbp} knuts.")
	if args == 3: # they're trying to convert wizard -> muggle
		try:
			gal = int(parts[1])
			sic = int(parts[2])
			knut = int(parts[3])
			usd = round(((gal*25) + (sic*1.47) + (knut*.05))*100)/100
			gbp = round(((gal*20.05) + (sic*1.18) + (knut*0.04))*100)/100
			return await message.channel.send(f"{message.author.mention}, {gal} galleons, {sic} sickles, and {knut} knuts is roughly equal to ${usd} or £{gbp}")
		except IndexError:
			pass
	else:
		return await message.channel.send(f"Hey {message.author.mention}, looks like you might be having trouble with the `convert` command! You can either supply a single number to go from USD/GBP to Wizarding Currency, or you can supply 3 numbers that correspond to Galleons, Sickles, and Knuts, respectively! Try something like `!convert 10 50 1` or `!convert 150`. Have a great day!")
	
# Joke - tell a cheezy joke!
async def joke(message):
	l("Running 'joke'")
	joke = random.choice(const.JOKES)
	await message.channel.send(joke[0])
	await asyncio.sleep(3)
	async with message.channel.typing():
		await asyncio.sleep(3)
		return await message.channel.send(joke[1])





###################################################
###				HELPER FUNCTIONS				###
###################################################

async def runner(command, message):
	# If we've made it here, the user is able to run the command and it's valid and in the right channel.
	# This part is sketch, but it works.
	c = command+'(message)'
	return await eval(c)

async def getUserFromName(message,name):
	# TODO: Figure out how to handle spaces in the username
	for user in message.guild.members:
		if user.name+"#"+user.discriminator == name:
			return user.id
	return None

async def getUserFromID(message,dID):
	for user in message.guild.members:
		if user.id == int(dID):
			return user
	return None

def reloadLibs():
	reload(db)
	reload(const)
	return