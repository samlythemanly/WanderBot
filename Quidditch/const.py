from types import SimpleNamespace

# Using SimpleNamespace to allow for dot notation
ROLES = SimpleNamespace(**{
        'ADMIN':'Admin',
        'MOD':'Moderator',
        'DEV':'Robot',
        'CONTRIBUTER':"Wanderbot's Friend",
        'ALL':'all'
})

STATUS_LIST = ["WATCHING: A Quidditch Game!"
        ]
ACTION_ENUM = {
        "PLAYING": 0,
        "STREAMING": 1,
        "LISTENING": 2,
        "WATCHING": 3
}

TRIGGER_SYMBOL = '\\'