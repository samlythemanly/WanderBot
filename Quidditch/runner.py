from importlib import reload ## DEBUGGING
import const
import logging
import asyncio
import re
import math
import classes.Game
from beautifultable import BeautifulTable


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
	action = parts[0] # what are they trying to do?
	if len(parts[1:]) > 1: 
		# There's extra stuff
		extras = parts[1:]
	else:
		extras = None

	#We also need to know information on who sent the message.
	player_id = message.author.id
	response = GM.addAction(
					playerID=player_id, 
					# house=player_team,
					action=action,
					extras=extras)
	# Check the status if it went through
	if not response['status']:
		return await message.delete()
	await message.channel.send(f"Accepted command: {action}")
	if response['extras']:
		return await message.channel.send('\n- '.join(response['extras']['action_log']))

	return




def reloadLibs():
	reload(const)
	reload(classes.Game)
	return