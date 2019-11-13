from classes.Ball import Ball
from classes.Player import Player
from classes.Action import Action
import asyncio

class Game(object):
	"""
	Game manager. Keeps track of everything.
	Discord Quidditch is a turn-based game. Each turn has the following phases in order:
		1. Upkeep Phase:
			- Resolve all actions from the previous turn in order.
			- Apply / Remove trait modifiers
			- Generate list of players who can perform actions this turn
			- Announce results of previous turn
			- [optional] Announce information about the Snitch.
		2. Action Phase:
			- During this phase, players have a chance to attempt an action that will get resolved next turn.
			- Actions must be valid
		3. End Turn Phase:
			- Decrement action cooldowns
			- Clean up and get ready for the next turn. 
	"""

	def __init__(self):
		self.players = []
		self.balls = self._init_balls()
		# self.score = {teamA:0,teamB:0}
		self.events = [] # keeps track of what is going on during each turn, to be resolved at the start of next turn
		self.turn = 0 # start at turn 0
		self.status = 0 # 0 is starting up, 1 is running.
		self.state = 'Starting up. Waiting for Player Roster to be loaded.'

	# Player is the discordID, action is a string, extras is a dict (Jersey number?)

	def addAction(self, playerID=None, action=None, extras=None, team=team):
		# For debugging only:
		print(playerID,action,extras)
		if action == 'end':
			return self.endTurn() # fall-down into a bunch of stuff
		player = self.getPlayerByDiscordID(playerID,team)
		if not player:
			print("Could not find player")
			return self.generateResponse(False,None) # Bad playerID
		# A player has attempted to do something, let's make sure they can.
		if not self.validateAction(player, action, extras, team):
			return self.generateResponse(False,None) # This is not allowed
		# This player can do that action, let's save it for the next upkeep phase
		event = (player,action,extras)
		# if action.type == 'instant':
		# 	self.events.append(event)
		# 	return self.endTurn() # fall-down into a bunch of stuff
		self.events.append(event)
		return self.generateResponse(True,None) # Successful, and did not trigger anything

	# TODO
	# UPKEEP PHASE:
	#	- Resolve all events from the previous turn in order.
	#	- Apply / Remove trait modifiers
	#	- Generate list of players who can perform actions this turn
	#	- Announce results of previous turn
	#	- [optional] Announce information about the Snitch.
	def upkeep(self):
		self.turn += 1 
		action_log = [] # Human readable logs to summarize what happened
		# Resolve events from previous turn
		# 'hit' will always be resolved last
		hits = [] # hold on to them for now
		quaffle_caught = False
		for event in self.events:
			# Okay let's handle each command...
			if event[1] == 'hit':
				hits.append(event)
				continue
			if event[1] == 'grab':
				if quaffle_caught:
					continue
				else:
					# Initially, it's the first person to catch the Quaffle, but later we want it to be random
					# This person caught the quaffle, change the owner.
					ball = self.getBallByName('quaffle')
					if ball.owner is None:
						ball.owner = event[0].characterID # assign it to this player.
						quaffle_caught = True # speed this up the next time the loop runs
						action_log.append(f"{event[0].name} has caught the Quaffle!")
				pass
			if event[1] == 'pass':
				# Now we're assuming that during validation, we made sure the player is holding the Quaffle.
				ball = self.getBallByOwner(event[0].characterID)
				# found the ball. let's change the owners now
				ball.owner = event[2].characterID
				action_log.append(f"{event[0].name} passed the Quaffle to {event[2].name}!")
			if event[1] == 'shoot':
				# Again, the assumption here is that this event is valid, and the player owns the quaffle
				action_log.append(f"{event[0].name} shoots the Quaffle towards the goal posts!")
				action_log.append("The Quaffle is now free to be grabbed!")
				ball = self.getBallByOwner(event[0].characterID)
				ball.owner = None # lose possesion of the ball
				# TODO: Handle the scoring event
				# ...


			## Will implement these later
			# if event[1] == 'search':
			# 	pass
			# if event[1] == 'foul':
			# 	pass
		# Okay that's the main loop, let's now handle the hits
		for event in hits:
			action_log.append(f"{event[0].name} hit's the Bludger towards {event[2].name}!")
			ball = self.getBallByOwner(event[0].characterID)
			ball.owner = None
			# TODO: Handle the damage.

		## TODO
		# Now handle the modifiers

		# Return the results
		extras = {'action_log':action_log}
		return self.generateResponse(True,extras)



	# TODO
	# End of turn ... decrement cooldowns for now I guess?
	def endTurn(self):
		for player in self.players:
			player.reduceCooldowns()
		return self.upkeep()

	# TODO
	# In order to validate the action we need to check a few things:
	#	- If the action involves a ball, can the player be in possesion of it, and is the ball free?
	#	- Is the player incapciated?
	#	- Is that action on cooldown?
	#	- Is this part of the action set for this player?
	#	- If there are extra args, make sure they make sense.
	def validateAction(self, player, action, extras, team):
		# First, check if the player can run this action
		if not player.hasAction(action):
			return False
		# Next, is the action on cooldown?
		if player.isActionOnCooldown(action): # Returns True if there's a cooldown
			print(f"Action {action} is on cooldown for {player.name}")
			return False
		### ACTIONS THAT REQUIRE SPECIAL POSESSION OF A BALL ###
		# For 'pass' and 'shoot', make sure the player owns the quaffle
		if action in ['pass','shoot']: 
			q = self.getBallByName('quaffle')
			if not q.owner == player.characterID:
				return False
		# If it's a 'hit' action, we need to make sure at least one bludger is open.
		if action == 'hit':
			bludgers = self.getBallByName('bludger')
			for bludger in bludgers:
				if bludger.owner is None:
					bludger.owner = player.characterID
					break
			else: # yep. A for/else loop. This entire code is a dark mark on humanity.
				print(f"{player.name} cannot use 'hit' because all bludgers are taken")
				return False
		# For 'grab', we need to make sure the quaffle is free.
		if action == 'grab':
			q = self.getBallByName('quaffle')
			if q.owner:
				print(f"{player.name} cannot grab the quaffle as it's not free")
				return False
		# Validate the extra args
		if extras:
			t_player = self.getPlayerByJersey(extras, team) #idk man. This should work?
			if not t_player:
				print(f"{player.name} tried to target an unknown player")
				return False



	def _init_balls(self):
		print("  Initializing Ball objects...")
		balls = []
		balls.append(Ball(name="quaffle"))
		balls.append(Ball("bludger"))
		balls.append(Ball("bludger"))
		balls.append(Ball("snitch"))
		print("    Done.")
		return balls

	def getState(self):
		return self.state

	def getBallByOwner(self,characterID):
		for ball in self.balls:
			if ball.owner == characterID:
				return ball

	def getBallByName(self, name):
		t = []
		for ball in self.balls:
			if ball.name == name:
				t.append(ball)
		if len(t) == 1: # oh god this is horrible please help me.
			return t[0]
		else:
			return t # If it's the bludger, return two balls

	def getPlayerByDiscordID(self, discID, team):
		print("looking for:",discID)
		for player in self.players:
			if player.discordID == discID and player.team.lower() == team.lower():
				print(f"Found {player.name}")
				return player
		return None

	def getPlayerByJersey(self, jerseyNumber, team):
		print("looking for:",jerseyNumber)
		for player in self.players:
			if player.jersey == jerseyNumber and player.team.lower() == team.lower():
				print(f"Found {player.name}")
				return player
		return None

	def generateResponse(self, status, extras):
		response = {}
		response['status'] = status
		response['extras'] = extras
		return response

	def addPlayers(self, raw_players):
		print("  Initializing Player objects...")
		players = []
		for p in raw_players:
			new_player = Player(name=p['name'], 
						role=p['role'], 
						number=p['jersey'], 
						team=p['house'], 
						characterID=p['charID'],
						stats=p['stats'],
						discordID=p['discordID'])
			players.append(new_player)
			print(f"    Added: {new_player}")
		print(f"    Done.")
		if len(players) == 14:
			self.players = players
			self.status = 'Players loaded, ready to play!'
		else:
			return self.generateResponse(False,{'error':'Not enough players loaded'})
		return self.generateResponse(True, None)

	# We need a way to summarize everything happening in the game right now
	# Who are the players on each team, who has the balls, what's the score.
	# TODO
	def getCurrentState(self):
		pass