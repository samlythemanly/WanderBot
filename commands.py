import random

COMMAND_PREFIXES = [
        'ping',
        'coin',
        'say',
]

async def pingPong(message):
	await message.channel.send('Pong!')

async def coinToss(message):
	if random.randint(0,1):
		await message.channel.send('Heads!')
	else:
		await message.channel.send('Tails!')

# async def adminSay(message):
# 	if "admin" in [x.name.lower() for x in message.author.roles] or "robot" in [x.name.lower() for x in message.author.roles]:
# 		# grab the channel they want to talk to. 
# 		parts = message.content.split(' ') #Get the first word of the message without the symbol
# 		channel = parts[1]
# 		msg = parts[2:]
# 		await 