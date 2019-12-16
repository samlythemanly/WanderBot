class Action(object):
    """docstring for Action"""

    def __init__(self, name, cooldown=0, t='normal', duration=0):
        self.name = name
        # self.roles = roles # maybe don't need this.
        self.cooldown = cooldown  # how many turns until this action can be used again
        self.type = t
        self.duration = duration  # How long this action lasts/triggers it's effect
        self.current_cooldown = 0  # Counts down from cooldown before it can used again
        self.current_step = 0  # Counts up to duration before executed
        self.preparing = False  # What's the state of the action?

    # Is this action on a cooldown? Return True if current_cooldown is greater than 0
    def onCooldown(self):
        return self.current_cooldown > 0

    # Update this action (end turn phase)
    # If there's an active cooldown, reduce it by 1
    # If there's an ongoing duration effect, increase the count, unless it's already at duration
    def update(self):
        # Is this action being prepared?
        if self.preparing:
            if self.current_step < self.duration:
                self.current_step += 1
                return
            # If the current_step is equal to duration, that means we should have executed this action already
            # and we should reset this action and trigger the cooldown
            if self.current_step == self.duration:
                self.preparing = False
                self.current_cooldown = self.cooldown
                self.current_step = 0

        # Normal action, if it's on cooldown reduce it by 1
        if self.onCooldown():
            self.current_cooldown -= 1

    # trigger action (upkeep phase)
    # Set the cooldown, or start the timer for the duration
    def trigger(self):
        if self.type == 'prepared':
            self.preparing = True
        else:
            self.current_cooldown = self.cooldown

    def __str__(self):
        return f"{self.name} | Cooldown remaining: {self.current_cooldown}"

    '''
     All possible actions
     Actions can be one of three types:
         1. Instant - Ends the turn and resolves before anything else.
         2. Normal - Single turn action, resolved at the start of the next turn
         3. Prepared - Multi-turn action, requires special logic as it spans multiple turns (duration)
     Actions have cooldowns -- number of turns before that action can be used again.
         - For 'prepared' actions, the cooldown starts after the action fully resolves, or is cancelled.
    
    ACTIONS = {
        # Seeker attempts to catch the Snitch
        "Catch": {
            "roles":['seeker'],
            "cooldown": 4,
            "type": 'prepared', 
            "duration": 2
        },
        # Any Player attempts to foul another player
        "Foul":{
            "roles":['seeker','chaser','beater','keeper'],
            "cooldown": 2,
            "type": 'instant'
        },
        # Chaser attempts to obtain a 'loose' quaffle
        "Grab":{
            "roles":['chaser'],
            "cooldown": 0,
            "type": 'normal'
        },
        # Beater attempts to hit bludger at another player
        "Hit":{
            "roles":['beater'],
            "cooldown": 2,
            "type": 'normal'
        },
        # Chaser/Keeper attempt to transfer ownership of ball to another
        "Pass":{
            "roles":['keeper','chaser'],
            "cooldown": 0,
            "type": 'normal'
        },
        # Keeper buffs their ability to block goal
        "Ready":{
            "roles":['keeper'],
            "cooldown": 4,
            "type": 'prepared',
            "duration": 3 #default
        },
        # Any player can rest to remove their debuffs (and buffs!)
        "Rest":{
            "roles":['seeker','chaser','beater','keeper'],
            "cooldown": 0,
            "type": 'prepared',
            "duration":3
        },
        # Seeker attempts to find the location/direction of the snitch
        "Search":{
            "roles":['seeker'],
            "cooldown": 5,
            "type": 'normal'
        },
        # Chaser attempts to score with the quaffle
        "Shoot":{
            "roles":['chaser'],
            "cooldown": 4,
            "type": 'normal'
        },
        #Any user can check what the status of their player is (will be PM'd)
        "Status":{
            "roles":['seeker','chaser','beater','keeper'],
            "cooldown": 0,
            "type": 'normal'
        },
        # Beater buffs their 'hit' ability
        "Target":{
            "roles":['beater'],
            "cooldown": 4,
            "type": 'prepared',
            "duration":2
        }

    }
'''
