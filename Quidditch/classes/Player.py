from .Action import Action
import wanderbot.db.quid_db as db

class Player(object):
	"""docstring for Player"""


	def __init__(self, name=None, role=None, number=None, team=None, characterID=None, discordID=None, stats=[]):
		self.name = name # The player's name
		self.role = role # "chaser", "beater", "keeper", or "seeker"
		self.jersey = number # Jersey number
		self.team = team # What house team do they belong to 
		self.characterID = characterID # unique character id
		self.discordID = discordID # DiscordID of the human who is controlling this player
		self.traits = [5,5,5,5] #Accuracy, Agility, Endurance, Strength
		self.setTraits(stats)
		self.modifiers = [0,0,0,0] # Modifiers are added to the trait before using it
		self.status = 'playing' # ['playing','reserve','ejected','injured','knocked out', 'preparing', 'resting']
		self.holding = None # What ball are they holding (if any)
		self.current_action = None
		self.cooldowns = {} # Store actions that are on cooldown, and for how long.
		self.actions = []

		self.initPlayerActions() # Create and add all the action objects

	# Set player traits
	def setTraits(self, stats):
		if len(stats) < 1:
			return
		if not sum(stats) == 20:
			return 
		else:
			self.traits = stats

	# TODO
	def reduceCooldowns(self):
		for action in self.actions:
			action.update()

	def isActionOnCooldown(self,actionName):
		for action in self.actions:
			if action.name == actionName:
				return action.onCooldown()
		return True # If we don't find the action, just return True lol

	def hasAction(self,actionName):
		for action in self.actions:
			if action.name == actionName:
				return True
		return False


	def initPlayerActions(self):
		# Figure out what role the player is, and call that function.
		if self.role == 'beater':
			self.initBeaterActions()
		elif self.role == 'chaser':
			self.initChaserActions()
		elif self.role == 'keeper':
			self.initKeeperActions()
		elif self.role == 'seeker':
			self.initSeekerActions()
		# Now add the shared actions
		self.initSharedActions()
		return

	def initBeaterActions(self):
		# Beater's actions are: Hit
		hit_action = Action(name='hit',cooldown=2)
		self.actions.extend([hit_action])

	def initChaserActions(self):
		# Chaser's actions are: Grab, Pass, Shoot
		grab_action = Action(name='grab',cooldown=0)
		pass_action = Action(name='pass',cooldown=0)
		shoot_action = Action(name='shoot',cooldown=4)
		self.actions.extend([grab_action, pass_action, shoot_action])

	def initKeeperActions(self):
		# Keeper's actions are: pass
		pass_action = Action(name='pass',cooldown=0)
		self.actions.extend([pass_action])

	def initSeekerActions(self):
		# Seeker's actions are: Search
		search_action = Action(name='search',cooldown=5)
		self.actions.extend([search_action])

	def initSharedActions(self):
		# Actions that everyone can use: Foul, Status
		foul_action = Action(name='foul',cooldown=2)
		status_action = Action(name='status',cooldown=0)
		self.actions.extend([foul_action, status_action])


	def __str__(self):
		return f"Character Name: {self.name} |  ID: {self.characterID} | Discord Player: {self.discordID}" 

# def main():

# 	p1 = Player("char1","Seeker",-1,"Ravenclaw",1,1234)
# 	p2 = Player("char2","Keeper",1,"Hufflepuff",2,5678)
# 	print(f"P1 cooldown: {p1.actions.Target}. P2 cooldown: {p2.actions.Target}")
# 	# p1.actions['Target']['cooldown'] = 7
# 	# print(f"P1 cooldown: {p1.actions['Target']['cooldown']}. P2 cooldown: {p2.actions['Target']['cooldown']}")

# if __name__ == '__main__':
# 	main()