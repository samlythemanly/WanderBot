from importlib import reload ## DEBUGGING
import random
import db
import const


ALL_ALLOWED_CHANNELS = ['bot-test']
SECRET_CHANNEL = ['temp']
QUIDDITCH = ['the-field']
ADMIN_ROLE = 'Admin'
MOD_ROLE = 'Moderator'

COMMANDS = {
		'reload': {
				'roles':['none'],
				'channels':ALL_ALLOWED_CHANNELS
				},
		'help': {
				'roles':['all'],
				'channels':ALL_ALLOWED_CHANNELS
				},
		'ping': {
				'roles':['all'],
				'channels':ALL_ALLOWED_CHANNELS
				},
		'coin': {
				'roles':['all'],
				'channels':ALL_ALLOWED_CHANNELS
				},
		'change_status':{
				'roles':[ADMIN_ROLE,MOD_ROLE],
				'channels':ALL_ALLOWED_CHANNELS
				},
	   	'favorite': {
	   			'roles':['none'],
	   			'channels':ALL_ALLOWED_CHANNELS
	   			},
	   	'link': {
	   			'roles':['none'],
	   			# 'roles':[ADMIN_ROLE,MOD_ROLE],
	   			'channels':ALL_ALLOWED_CHANNELS
	   			},
	   	'find': {
	   			'roles':['none'],
	   			# 'roles':[ADMIN_ROLE,MOD_ROLE],
	   			'channels':ALL_ALLOWED_CHANNELS
	   			},
	   	'activity': {
	   			'roles':[ADMIN_ROLE],
	   			# 'roles':[ADMIN_ROLE,MOD_ROLE],
	   			'channels':ALL_ALLOWED_CHANNELS
	   			},
	   	'mock': {
	   			'roles':['all'],
	   			# 'roles':[ADMIN_ROLE,MOD_ROLE],
	   			'channels':SECRET_CHANNEL
	   			},
	   	'compliment': {
	   			'roles':['all'],
	   			# 'roles':[ADMIN_ROLE,MOD_ROLE],
	   			'channels':SECRET_CHANNEL
	   			}
}


# Help Command 
#	Lists all the commands the user is allowed to run
async def help(message):
	# Get the user roles
	allowed_commands = []
	for command in COMMANDS:
		if COMMANDS[command]['roles'][0] == 'all':
			allowed_commands.append(command)
		else:
			for role in COMMANDS[command]['roles']:
				if role in [str(r) for r in message.author.roles]:
					allowed_commands.append(command)
	return await message.channel.send(f"Hi {message.author.mention}, you can run the following commands: {', '.join([f'`{x}`' for x in allowed_commands])}. Remember to add a '!' before the command you want :)")


# Ping Pong
#	Simply reply 'Pong!' to the users message. Mostly used to check if the bot is up.
async def ping(message):
	return await message.channel.send('Pong!')

# Coin Toss
#	Flips a 'psudo-fair' coin
async def coin(message):
	if random.randint(0,1):
		await message.channel.send('Heads!')
	else:
		await message.channel.send('Tails!')

# Favorite User
#	 Returns the user who last reacted to WanderBot.
async def favorite(message,current_favorite_user):
	if current_favorite_user:
		return await message.channel.send(f"{current_favorite_user.display_name} is my current favorite person!")
	else:
		return await message.channel.send(f"I don't have a current favorite person right now!")

# Link User to Character
#	First argument is the discordID (int), all other arguments are comma delimeted characterIDs
#	ex: !link 12345456 24, 25, 26
async def link(message):
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
	user_to_mock = message.mentions[0]
	if not user_to_mock:
		return
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
			return await message.channel.send(f'{response} - {m.author.mention}')

async def compliment(message):
	try:
		user_to_compliment = message.mentions[0]
	except IndexError:
		return await message.channel.send(f"I don't know who you want me to compliment, so I'll compliment myself. I'm a good bot and I do good things. Thanks {message.author.mention}!")
	compliment = random.choice(const.COMPLIMENTS)
	return await message.channel.send(f"Hey {user_to_compliment.mention}, {compliment}")






###################################################
###				HELPER FUNCTIONS				###
###################################################

async def runner(command, message):
	# If we've made it here, the user is able to run the command and it's valid.
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