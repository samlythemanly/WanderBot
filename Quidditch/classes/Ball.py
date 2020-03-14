class Ball(object):
    """Generic Ball Object
        Can be either:
        - (1) Quaffle
        - (2) Bludger
        - (3) Snitch """

    def __init__(self, name=None):
        self.name = name
        self.owner = None  # Owner is the player who possesses the ball (characterID)

    def __str__(self):
        return f"Ball: {self.name} | Owner: {self.owner}"

# Set up internal variables for a Quaffle
# def makeQuaffle(self):
#   self.value = 10
#   self.valid_owners = ['chaser','keeper']

# # Set up internal variables for a Bludger
# def makeBludger(self):
#   self.value = 0
#   self.valid_owners = ['beater']
#   self.collidable = True

# # Set up internal variables for a Snitch
# def makeSnitch(self):
#   self.value = 150
#   self.valid_owners = ['seeker']
#   self.visibility = 0.0
