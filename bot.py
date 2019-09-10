import const
from private_info import API_TOKEN, BOT_ID
import discord
import commands

client = discord.Client()

######################
##       TODO       ##
######################
#	- adminSay command
#	- random favorite person in channel
#   - Quidditch commands
#   - Statuses and status rotation
#   - More easter eggs?
#	- fuckin everything else


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

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
    	await parseMessage(message)

   	# Let's get the easter eggs out of the way...
   	# We only do this if they're not trying to write a command.
    else:
    	if 'wanderbot' in message.content.lower():
    		await message.add_reaction('👋')
    	if 'drama' in message.content.lower():
    		await message.add_reaction('👀')
    	if 'good bot' in message.content.lower():
    		await message.add_reaction('😊')
    	if message.mentions:
    		for mention in message.mentions:
    			if mention.id == BOT_ID: # our own ID
    				await message.add_reaction('👋')

@client.event
async def on_reaction_add(reaction, user):
	if reaction.message.author == client.user: #They reacted to us!
		return # Coming soon?

async def parseMessage(message):
	# What's the command?
	prefix = message.content.split(' ')[0][1:].lower() #Get the first word of the message without the symbol
	if prefix in commands.COMMAND_PREFIXES:
		if prefix == 'ping':
			return await commands.pingPong(message)
		if prefix == 'coin':
			return await commands.coinToss(message)

	else:
		print(f"Invalid Command: {prefix}")
		#invalidCommand(prefix)






client.run(API_TOKEN)