from importlib import reload ## DEBUGGING
import const
import logging
import asyncio
import re
import math
import classes.Game
from beautifultable import BeautifulTable
import db


'''

Runner is an intermediate module for communicating with the Game Manager (GM)

'''
async def newAction(message, GM):
	# So it's an action. Let's figure out what team it's for
	if not GM:
		print("NO GAME MANAGER OBJECT")
		return -1
	player_team = None
	if 'slytherin' in message.content.lower():
		player_team = const.HOUSE.SLYTHERIN
	elif 'gryffindor' in message.content.lower():
		player_team = const.HOUSE.GRYFFINDOR
	elif 'ravenclaw' in message.content.lower():
		player_team = const.HOUSE.RAVENCLAW
	else:
		player_team = const.HOUSE.HUFFLEPUFF

	# What else does the game manager want?
	# We should be nice and parse the action and addition args as well
	parts = message.content.split(' ')[1:] # skip the emoji we already know it

	### BEGIN DEBUGGING
	fake_discordID = GM.getPlayerDiscordIDByCharID(int(parts[0])) # We will pass in the characterID of who we're trying to be.
	if not fake_discordID:
		print(f"Debugging: Could not find discordID for {parts[0]}")
		return #?
	parts = parts[1:]
	print(f"Debugging: Found discordID for {parts[0]}")
	### END DEBUGGING

	action = parts[0] # what are they trying to do?
	if len(parts) > 1: 
		# There's an extra argument (target_player)
		try:
			t_player = int(parts[1]) # The human players will be going off JERSY numbers, not charIDs. 
		except ValueError:
			print(f"Message: `{parts}` failed integer parsing for target_player")
			return await message.delete()
	else:
		t_player = None

	#We also need to know information on who sent the message.
	# author_id = message.author.id
	response = GM.addAction(
					discordID=fake_discordID, 
					team=player_team,
					action=action,
					t_player=t_player)
	print(f"**Response: {response}")
	# Check results:
	#	response['status'] is boolean if the command was valid or not
	#	response['extras'] is populated if the command caused the turn to be over.
	if not response['status']:
		return await message.delete()
	await message.channel.send(f"Accepted command: `{message.content}`")
	if response['extras']:
		update_log = '\n- '+'\n- '.join(response['extras']['action_log'])
		return await message.channel.send('\n- '.join(response['extras']['action_log']))

	return

async def loadRoster(message,GM):
	# Parse the big message to create the player objects.
	try:
		lines = message.content.split('\n')[1:] # ignore the first row with the command
		players = []
		for line in lines:
			l = re.sub('\s{4}', ',', line).split(',') # Copy/pasting from Google Sheets results in 4-space delimited lines
			# Okay we have the rows, here is the expected structure:
			#	0. Character Name,
			#	1. Character ID,
			#	2. House,
			#	3. Position,
			#	4. Jersy #,
			#	5. Accuracy,
			#	6. Agility,
			#	7. Endurance,
			#	8. Strength
			print(f"Looking for DiscordID for characterID: {l[1]}...",end='')
			discordID = await db.getDiscordFromCharacterID(l[1])
			print(f"Looking for DiscordID for characterID: {l[1]}...found: {discordID}")
			if not discordID:
				print(f"Error on characterID: {l[1]}")
			player = {
				'name':l[0],
				'charID':int(l[1]),
				'house':validateHouse(l[2]),
				'role':l[3].lower(),
				'jersey':int(l[4]),
				'stats':[int(s) for s in l[5:]],
				'discordID':discordID
				}
			players.append(player)
	except IndexError:
		await message.channel.send(f"Something went wrong trying to parse the message. Try again?")
		return False
	# Call the GameManager to load the players.
	response = GM.addPlayers(players)
	if response['status']:
		# await message.channel.send(f"Successfully loaded all players.")
		return True
	else:
		await message.channel.send(f"Error: {response['extras']['error']}")
		return False

# We will be creating a scoreboard message which the Game Manager will keep track of.
async def createScoreboard(message, game_channel):
	return True

	



def validateHouse(house):
	if house.lower() == 'slytherin':
		return const.HOUSE.SLYTHERIN
	elif house.lower() == 'ravenclaw':
		return const.HOUSE.RAVENCLAW
	elif house.lower() == 'gryffindor':
		return const.HOUSE.GRYFFINDOR
	else:
		return const.HOUSE.HUFFLEPUFF

def reloadLibs():
	reload(const)
	reload(classes.Game)
	return