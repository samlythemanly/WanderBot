from importlib import reload ## DEBUGGING
import random
from db.db import *
import const, audit
import logging
import asyncio
import re
from beautifultable import BeautifulTable

l = logging.info

PRODUCTION_CHANNELS = [
  'general',
  'eyebrow-waggling-stuff',
  'pics-and-gif-spam',
  'meme-central',
  'sick-music-bruh',
  'video-killed-the-radio-star',
  'bot-test',
  'feature-requests',
  'bugz',
  'char-dev',
  'iso',
  'gushers',
  'staff-has-fun-sometimes',
  'staff-general',
  'wanderbots-void']
TEST_CHANNELS = ['bot-test','feature-requests','temp','staff-general','wanderbots-void']
STAFF_CATEGORIES = ['Bot Playground',
  'The Magic Treehouse'
  ]
SECRET_CHANNEL = ['temp']
QUIDDITCH = ['the-field']
ROLES=const.ROLES

COMMANDS = {
  # General Commands for everyone
    'help': {
        'roles':[ROLES.ALL],
        'channels':PRODUCTION_CHANNELS,
        'hidden':False
        },
    'ping': {
        'roles':[ROLES.ALL],
        'channels':PRODUCTION_CHANNELS,
        'hidden':False
        },
    'coin': {
        'roles':[ROLES.ALL],
        'channels':PRODUCTION_CHANNELS,
        'hidden':False
        },
       'mock': {
           'roles':[ROLES.ALL],
           'channels':PRODUCTION_CHANNELS,
           'hidden':True
           },
       'compliment': {
           'roles':[ROLES.ALL],
           'channels':PRODUCTION_CHANNELS,
           'hidden':True
           },
       'convert': {
           'roles':[ROLES.ALL],
           'channels': PRODUCTION_CHANNELS,
           'hidden':False
           },
       'joke': {
           'roles':[ROLES.ALL],
           'channels': PRODUCTION_CHANNELS,
           'hidden':True
           },
       'halp': {
           'roles':[ROLES.ALL],
           'channels': PRODUCTION_CHANNELS,
           'hidden':True
           },
    'activity': {
           'roles':[ROLES.ALL],
           'channels':PRODUCTION_CHANNELS,
           'hidden':False
           },
  # Admin / Mod commands
       'change_status':{
        'roles':[ROLES.ADMIN,ROLES.MOD],
        'channels':PRODUCTION_CHANNELS,
        'hidden':True
        },
  # Dev commands / in development commands
    'favorite': {
           'roles':[ROLES.DEV],
           'channels':TEST_CHANNELS,
           'hidden':True
           },
       'link': {
           'roles':[ROLES.ADMIN],
           # 'roles':[ADMIN_ROLE,MOD_ROLE],
           'channels':TEST_CHANNELS,
           'hidden':True
           },
       'find': {
           'roles':[ROLES.ADMIN],
           # 'roles':[ADMIN_ROLE,MOD_ROLE],
           'channels':TEST_CHANNELS,
           'hidden':True
           },
       'reload': {
        'roles':[ROLES.ADMIN],
        'channels':TEST_CHANNELS,
        'hidden':True
        },
    'debug': {
        'roles':[ROLES.DEV],
        'channels':TEST_CHANNELS,
        'hidden':True
        },
       'archive': {
        'roles':[ROLES.ADMIN],
        'channels':TEST_CHANNELS,
        'hidden':True
        },
       'archived': {
        'roles':[ROLES.ADMIN],
        'channels':TEST_CHANNELS,
        'hidden':True
        },
    'unarchive': {
        'roles':[ROLES.ADMIN],
        'channels':TEST_CHANNELS,
        'hidden':True
        },
    'probation': {
        'roles':[ROLES.DEV],
        'channels':TEST_CHANNELS,
        'hidden':True
        },
    'reset_monthly_post_count': {
        'roles': [ROLES.DEV],
        'channels': TEST_CHANNELS,
        'hidden': True
        },
      'reset_all_monthly_post_counts': {
        'roles': [ROLES.DEV],
        'channels': TEST_CHANNELS,
        'hidden': True
        },
  # Special commands for Quidditch!
    'quidditch': {
        'roles':[ROLES.DEV],
        'channels':TEST_CHANNELS,
        'hidden':True
        },
    'end_quidditch': {
        'roles':[ROLES.DEV],
        'channels':TEST_CHANNELS,
        'hidden':True
        },
}


# Help Command
#  Lists all the commands the user is allowed to run
async def help(message):
  l("Running 'help'")
  # Get the user roles
  allowed_commands = []
  for command in COMMANDS:
    if COMMANDS[command]['hidden']:
      continue;
    if COMMANDS[command]['roles'][0] == 'all':
      allowed_commands.append(command)
    else:
      for role in COMMANDS[command]['roles']:
        if role in [str(r) for r in message.author.roles]:
          allowed_commands.append(command)
  return await message.channel.send(f"Hi {message.author.mention}, you can run the following commands: {', '.join([f'`{x}`' for x in allowed_commands])}. Remember to add a '!' before the command you want :)")

# Halp Command
#  Lists all the hidden commands the user is allowed to run
async def halp(message):
  l("Running 'halp'")
  # Get the user roles
  allowed_commands = []
  for command in COMMANDS:
    if COMMANDS[command]['hidden']:
      if COMMANDS[command]['roles'][0] == 'all':
        allowed_commands.append(command)
      else:
        for role in COMMANDS[command]['roles']:
          if role in [str(r) for r in message.author.roles]:
            allowed_commands.append(command)
  return await message.channel.send(f"Surprise {message.author.mention}! You can run the following _*SPECIAL*_ commands: {', '.join([f'`{x}`' for x in allowed_commands])}. Remember to add a '!' before the command you want :)")


# Ping Pong
#  Simply reply 'Pong!' to the users message. Mostly used to check if the bot is up.
async def ping(message):
  l("Running 'pong'")
  return await message.channel.send('Pong!')

# Coin Toss
#  Flips a 'psudo-fair' coin
async def coin(message):
  l("Running 'coin'")
  if random.randint(0,1):
    await message.channel.send('Heads!')
  else:
    await message.channel.send('Tails!')

# Favorite User
#   Returns the user who last reacted to WanderBot.
# TODO: Fix this
async def favorite(message,current_favorite_user):
  l("Running 'favorite'")
  if current_favorite_user:
    return await message.channel.send(f"{current_favorite_user.display_name} is my current favorite person!")
  else:
    return await message.channel.send(f"I don't have a current favorite person right now!")

# Link User to Character, or link Player to DiscordID
#  Two execution paths:
#  1. Link User to character(s) - First argument is the discordID (int), all other arguments are comma delimeted characterIDs
#    ex: !link 123456 24, 25, 26
#  2. Link User to custom name - First argument is the discordID (int), only other argument is the player name
#    ex: !link 123456 Charles
async def link(message):
  l("Running 'link'")
  parts = message.content.split(' ') #split on space first
  if len(parts) < 3: #minimum number of required args
    return await message.channel.send(f"Whoops! Looks like I need a little more info there...try again?")

  prefix = parts[0] # The original command. Ignore it
  discordID = parts[1] # The id of the person to link to.

  # First, validate the ID and get the user.
  target = await getUserFromID(message,discordID)
  if not target:
    # Invalid discordID, abort.
    return await message.channel.send(f"Sorry, I can't find anyone with that name, try again?")

  if re.search(r"[a-zA-Z]",parts[2]): # Checks for letters in the second argument, which means we're going down path (2)
    # Update the players table to link this discordID to the player name
    if len(parts) != 3:
      return await message.channel.send(f"Oops! Something went wrong. If you're trying to link a discord ID to player name, here's an example of the command: `!link 124345 WanderBot`")
    player_name = parts[2]
    # if re.search(r"\d",player_name):
    #   return await message.channel.send(f"Sorry, player names cannot contain numbers. Don't blame me, blame society.")

    #whew okay let's keep going.
    operation,row_count = await linkDiscordToPlayer(target.id, player_name)
    if operation == 'update': # we updated their name
      await message.channel.send(f"Updated the name of ID {discordID} to {player_name}")
      return await logAuditEvent(message,'link player')
    else:
      await message.channel.send(f"Linked ID {discordID} to player name: {player_name}")
      return await logAuditEvent(message,'link player')

  # Okay let's go down the other path now (1), linked a discord ID to characters
  charList = ' '.join(parts[2:]).replace(' ','').split(',')
  rows_updated = await linkDiscordToCharacters(target.id,charList)
  await initNewCharacter(charList)
  if rows_updated > 0:
    # We updated some rows, let's see what they are.
    updated_chars = await getCharactersFromIDs(charList)
    if updated_chars:
      print(f"Updated Chars: {updated_chars}")
      response = f"Linked {target.display_name} to the following character(s):"
      for c in updated_chars:
        response += f"\n- {c}"
    await message.channel.send(response)
    return await logAuditEvent(message,'link character')
  else:
    return await message.channel.send(f"Uh-oh. Something went wrong trying to link. Double-check the command and try again?")

async def reset_monthly_post_count(message):
  l("Running 'reset_monthly_post_count'")
  parts = message.content.split(' ') #split on space first
  if len(parts) < 3: #minimum number of required args
    return await message.channel.send(f"Whoops! Looks like I need a little more info there...try again?")
  prefix = parts[0] # The original command. Ignore it
  charID = parts[1] # The id of the character to set the posts of.
  postCount = parts[2] # The new post count for the character.
  charInfo = await findUserFromID(charID)

  if charInfo:
    result = updateCharacterMonthlyPostCount(charID, postCount)
    if not result:
      return await message.channel.send(f"Sorry, updating the monthly post count didn't work. Check the spelling of the user or that the new post count is a valid number.")
    return await message.channel.send(f"Successfully updated character ID {charID} with new post count {postCount}!")

# Resets all character post counts for this month
async def reset_all_monthly_post_counts(message):
  l("Running 'reset_all_monthly_post_counts")
  result = resetAllCharacterMonthlyPostCounts()
  if not result:
      return await message.channel.send(f"Sorry, resetting all post counts didn't work. Please ping the Wanderbot doctor.")
  return await message.channel.send(f"Successfully reset all character monthly post counts!")


# Find Character
#  Searches the db for a character and returns info about them
#  ex. !find 3
async def find(message):
  l("Running 'find'")
  charID = await parseCharID(message)
  charInfo = await findUserFromID(charID)
  return await message.channel.send(
    f"Character ID: {charInfo['ID']}\n"
    f"Character name: {charInfo['name']}\n"
    f"Total posts: {charInfo['total_posts']}\n"
    f"Posts this month: {charInfo['posts_this_month']}\n"
    f"On probation? {'Yes' if int(charInfo['on_probation']) > 0 else 'No'}")

# Activity Check
#  Takes a player name and returns the status of all their characters.
#  If it's Staff, then respond in that channel, if it's a normal user, PM them.
#  Additionally, delete the message if it's non-Staff, and log it in the wanderbots-void channel
#  ex. !activity Charles
async def activity(message):
  l("Running 'activity'")
  parts = message.content.split(' ') #split on space first
  player_id = message.author.id # default to their id first
  if isStaff(message) and len(parts) > 1 and str(message.channel.category) in STAFF_CATEGORIES: # They're asking for someone else's characters (must be staff)
    #They supplied a player name, so we should return all active characters for that player.
    result = await getIDfromName(parts[1])
    if not result:
      return await message.channel.send(f"Sorry, couldn't find a player with the name: {parts[1]}. Check the spelling or link a name to a discord ID using `!link`")
    player_id = result['discordID']

  # So we now know it's a valid ID, let's pull all the characters for that player.
  chars = await getPlayerCharacters(player_id)
  if not chars:
    return await message.channel.send(f"Whelp, looks like I couldn't find any characters ¯\\_(ツ)_/¯")

  paginator = []
  table = BeautifulTable()
  # Initiate a counter for pagination. We'll paginate on the fly. Max rows is 10.
  counter = 0
  table.column_headers = ["Character", "Total Posts", "Posts this month", "On Probation?"]
  for char in chars:
    counter += 1
    n = char['name']
    tp = char['total_posts']
    tpm = char['posts_this_month']
    p = 'Yes' if int(char['on_probation']) > 0  else 'No'
    table.append_row([n,tp,tpm,p])
    if counter == 10:
      paginator.append(table)
      table = BeautifulTable()
      table.column_headers = ["Character", "Total Posts", "Posts this month", "On Probation?"]
      counter = 0
  if len(table) > 0:
    paginator.append(table)

  # return await message.author.send(f"```{table}```")

  #Okay now we have all the info. Now we decide if we need to respond in the channel or PM the user.
  if isStaff(message) and str(message.channel.category) in STAFF_CATEGORIES:
    return await sendPaginatedTable(paginator, "Here ya go!", message.channel)
  else:
    # This is going to get PM'd, so let's delete their message once we PM them.
    header = f"Hey {message.author.name} here are your characters' activities!"
    await sendPaginatedTable(paginator, header, message.author)
    # Delete the message
    await message.delete()
    # log it in the wanderbots-void channel
    return await logAuditEvent(message,'activity')



# Mock the last tagged user's message
#  Pretty self explanitory
async def mock(message):
  l("Running 'mock'")
  try:
    user_to_mock = message.mentions[0]
  except IndexError:
    return await message.channel.send(f"There's no one tagged to mock! Looks like the only fool here is you, {message.author.mention}!")
  if not user_to_mock:
    return
  if user_to_mock.id == 617172295902822415 and random.choice(range(15)) == 10:
    return await message.channel.send(f"WANDERBOT IS TOO POWERFUL TO BE MOCKED, MORTAL.")

  async for m in message.channel.history():
    if m.author == user_to_mock:
      response = ''
      flag = random.randint(0,1)
      for char in m.content:
        if flag:
          response += char.lower()
          flag = 0
        else:
          response += char.upper()
          flag = 1
      return await message.channel.send(f'"{response}" - {m.author.mention}')

# Compliment the tagged user.
async def compliment(message):
  l("Running 'compliment'")
  try:
    user_to_compliment = message.mentions[0]
  except IndexError:
    return await message.channel.send(f"I don't know who you want me to compliment, so I'll compliment myself. I'm a good bot and I do good things. Thanks {message.author.mention}!")
  compliment = random.choice(const.COMPLIMENTS)
  return await message.channel.send(f"Hey {user_to_compliment.mention}, {compliment}")

# Convert currencies
#  If 1 argument is given, convert from usd/gbp to wizard
#  If 3 arguments are given, convert to usd/gbp
#  Else, return a helpful message
async def convert(message):
  l("Running 'convert'")
  parts = re.sub('[£$,]','',message.content).split(' ')
  args = len(parts[1:])
  # Which direction are they trying to convert?
  if args == 1: # they're trying to convert muggle -> wizard
    #This is going to get ugly.
    base = float(parts[1])
    gal_usd = round(base/25)
    gal_gbp = round(base/20.05)
    t_usd = base%25
    t_gbp = base%20.05
    sic_usd = round(t_usd/1.47)
    sic_gbp = round(t_gbp/1.18)
    t_usd = t_usd%1.47
    t_gbp = t_gbp%1.18
    knut_usd = round(t_usd/0.05)
    knut_gbp = round(t_gbp/0.04)
    return await message.channel.send(f"{message.author.mention}, ${base:.2f} is roughly equal to {gal_usd} galleons, {sic_usd} sickles, and {knut_usd} knuts.\nBut if you're from across the pond, then £{base:.2f} is roughly equal to {gal_gbp} galleons, {sic_gbp} sickles, and {knut_gbp} knuts.")
  if args == 3: # they're trying to convert wizard -> muggle
    try:
      gal = int(parts[1])
      sic = int(parts[2])
      knut = int(parts[3])
      usd = round(((gal*25) + (sic*1.47) + (knut*.05))*100)/100
      gbp = round(((gal*20.05) + (sic*1.18) + (knut*0.04))*100)/100
      return await message.channel.send(f"{message.author.mention}, {gal} galleons, {sic} sickles, and {knut} knuts is roughly equal to ${usd} or £{gbp}")
    except IndexError:
      pass
  else:
    return await message.channel.send(f"Hey {message.author.mention}, looks like you might be having trouble with the `convert` command! You can either supply a single number to go from USD/GBP to Wizarding Currency, or you can supply 3 numbers that correspond to Galleons, Sickles, and Knuts, respectively! Try something like `!convert 10 50 1` or `!convert 150`. Have a great day!")

# Joke - tell a cheezy joke!
async def joke(message):
  l("Running 'joke'")
  joke = random.choice(const.JOKES)
  await message.channel.send(joke[0])
  await asyncio.sleep(3)
  async with message.channel.typing():
    await asyncio.sleep(3)
    return await message.channel.send(joke[1])

async def archive(message):
  l("Running 'archive'")
  charID = await parseCharID(message)
  charInfo = await findUserFromID(charID)
  archived = await archiveCharacterByID(charID)
  if not archived:
    return await message.channel.send(f"Character with ID {charID} is archived already!")
  await message.channel.send(f"{charInfo['name']} is now sleeping ZzZz...\n")
  return await logAuditEvent(message,'archive')

async def unarchive(message):
  # TODO: When a character is un-archived, set probation to True
  l("Running 'unarchive'")
  charID = await parseCharID(message)
  charInfo = await findUserFromID(charID)
  unarchived = await unarchiveCharacterByID(charID)
  if not unarchived:
    return await message.channel.send(f"Character with ID {charID} is not archived, use !archived to see who is archived.")
  await message.channel.send(f"{charInfo['name']} is now alive!\n")
  return await logAuditEvent(message,'link')

async def probation(message):
  l("Running 'probation'")
  probation = await getCharactersOnProbation()
  if not probation:
    return await message.channel.send(f"Could not find any characters on probation. Woo!")

  table = BeautifulTable()
  table.column_headers = ["id", "Name"]
  for char in probation:
    i = char['ID']
    name = char['name']
    table.append_row([i,name])

  header = f"** Here are the characters on probation :( **"
  return await message.channel.send(f"{header}```{table}```")

async def archived(message):
  l("Running 'archived'")
  archived = await getCharactersOnArchived()
  if not archived:
    return await message.channel.send(f"Could not find any characters that are archived. Woo!")

  table = BeautifulTable()
  table.column_headers = ["id", "Name"]
  for char in archived:
    i = char['ID']
    name = char['name']
    table.append_row([i,name])

  header = f"** Here are the characters that are archived ...I mean asleep ZzZz **"
  return await message.channel.send(f"{header}```{table}```")

#General debugging command, used by dev only
async def debug(message):
  return await message.author.send(f"{message.channel}")



###################################################
###        HELPER FUNCTIONS        ###
###################################################

async def runner(command, message):
  # If we've made it here, the user is able to run the command and it's valid and in the right channel.
  # This part is sketch, but it works.
  c = command+'(message)'
  return await eval(c)

async def getUserFromName(message,name):
  # TODO: Figure out how to handle spaces in the username
  for user in message.guild.members:
    if user.name+"#"+user.discriminator == name:
      return user.id
  return None

async def getUserFromID(message,dID):
  for user in message.guild.members:
    if user.id == int(dID):
      return user
  return None

async def findUserFromID(charID):
  charInfo = await getCharacterFromID(charID)
  if not charInfo:
    return await message.channel.send(f"Could not find a character with ID {charID}. Try again?")
  return charInfo

async def parseCharID(message):
  try:
    parts = message.content.split(' ') #split on space first
    prefix = parts[0]
    charID = parts[1]
  except IndexError:
    return await message.channel.send(f"No ID supplied! Format should be `!<command> <character ID>`, example: `!find 2`")
  return charID


async def sendPaginatedTable(paginator, header, destination):
  async with destination.typing():
    # If there are less than 10 entries, just return the table
    if len(paginator) < 2:
      return await destination.send(f"** {header} **\n```{paginator[0]}```")
    # Need to return multiple messages
    header = f"** {header}\nPage 1/{len(paginator)}**"
    await destination.send(f"{header}\n```{paginator[0]}```") #return the first page
    ctr = 2
    for table in paginator[1:]:
      header = f"** Page {ctr}/{len(paginator)}**"
      ctr += 1
      await destination.send(f"{header}\n```{table}```") #return the next page
    return


# We want to keep an audit log for all commands that cause updates to the Database.
#  Also for user's activity checks
async def logAuditEvent(message, command):
  for ch in message.guild.channels:
      if str(ch) == const.AUDIT_CHANNEL:
        return await ch.send(f"{'-'*20}\n{message.author.name} called `{command}` in channel '{message.channel}'.")

def isStaff(message):
  if 'Robot' in [str(r) for r in message.author.roles]:
    return True
  # Check the user's role for this command.
  staff_roles = [ROLES.ADMIN,ROLES.MOD]
  for role in message.author.roles:
    if str(role) in staff_roles:
      return True
  return False

def reloadLibs():
  reload(db)
  reload(const)
  reload(audit)
  return
