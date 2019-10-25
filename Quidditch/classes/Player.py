import copy

class Player(object):
	"""docstring for Player"""


	def __init__(self, name, role, number, team, characterID, userID):
		self.name = name # The player's name
		self.role = role # "chaser", "beater", "keeper", or "seeker"
		self.number = number # Jersey number
		self.team = team # What house team do they belong to 
		self.characterID = characterID # unique character id
		self.userID = userID # DiscordID of the human who is controlling this player
		self.traits = [5,5,5,5] #Accuracy, Agility, Endurance, Strength
		self.modifiers = [0,0,0,0] # Modifiers are added to the trait before using it
		self.status = 'playing' # ['playing','reserve','ejected','injured','knocked out', 'preparing', 'resting']
		self.holding = None # What ball are they holding (if any)
		self.current_action = None
		self.cooldowns = {} # Store actions that are on cooldown, and for how long.
		self.actions = copy.deepcopy(Player.ACTIONS)

	# Set player traits
	def setTraits(self, traits):
		if not sum(traits) == 20:
			return False
		else:
			self.traits = traits

	def reduceCooldowns(self):
		for action in 

def main():

	p1 = Player("Bijan","Seeker",-1,"Ravenclaw",1,1234)
	p2 = Player("Izzy","Keeper",1,"Hufflepuff",2,5678)
	print(f"P1 cooldown: {p1.actions.Target}. P2 cooldown: {p2.actions.Target}")
	# p1.actions['Target']['cooldown'] = 7
	# print(f"P1 cooldown: {p1.actions['Target']['cooldown']}. P2 cooldown: {p2.actions['Target']['cooldown']}")

if __name__ == '__main__':
	main()