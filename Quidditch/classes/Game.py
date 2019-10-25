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

	def __init__(self, players, balls, teamA, teamB):
		self.players = players
		self.balls = balls
		self.score = {teamA:0,teamB:0}
		self.actions_this_turn = [] # keeps track of what is going on during each turn
		self.turn = 0 # start at turn 0

	def addAction(player, action):
		# A player has attempted to do something, let's make sure they can.
		if not self.validateAction(player, action):
			return False # This is not allowed
		# This player can do that action, let's save it for the next upkeep phase
		if action.type == 'instant':
			self.actions_this_turn.append(action)
			self.endTurn()
			return True # Successful
		self.actions_this_turn.append(action)
		return True # Successful

	# UPKEEP PHASE
	def upkeep():
		# Resolve actions from previous turn
		