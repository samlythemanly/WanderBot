'''
Database Query Engine
	Handles all DB interactions.
'''
import mysql.connector
import asyncio
from functools import wraps
from private_info import DB_HOST, DB_USER, DB_PASSWORD, DB_CATALOG

db = mysql.connector.connect(
	host=DB_HOST,
	user=DB_USER,
	passwd=DB_PASSWORD,
	database=DB_CATALOG
)

cur = db.cursor(dictionary=True, buffered=True)


# Writing a function decorator to refresh the DB every time a db function is called.
# Trying to get around the error of the db object disconnecting after some time
def initConn(f):
	@wraps(f)
	async def refreshDB(*args, **kwargs):
		db.reconnect()
		cur = db.cursor(dictionary=True, buffered=True)
		return await f(*args, **kwargs)
	return refreshDB

###################################################
###				READ-ONLY COMMANDS				###
###################################################

@initConn
async def getCharacterFromID(charID):
	sql = f'SELECT * from Characters where ID={int(charID)}'
	cur.execute(sql)
	res = cur.fetchone()
	db.commit()
	if res:
		return res
	return await None

@initConn
async def getCharactersFromIDs(charIDs):
	sql = f"SELECT name FROM Characters WHERE ID in ({','.join(charIDs)})"
	cur.execute(sql)
	res = cur.fetchall()
	db.commit()
	if res:
		return [c['name'] for c in res]
	else:
		return None

@initConn
async def getIDfromName(playerName):
	sql = f"SELECT * from Players where LOWER(name) = '{playerName.lower()}'"
	cur.execute(sql)
	res = cur.fetchone()
	db.commit()
	if res:
		return res
	return None

@initConn
async def getPlayerCharacters(playerID):
	sql = (f"select c.name, c.total_posts, c.posts_this_month, c.on_probation"
	f" from Characters c left join Players p on c.discordID = p.discordID"
	f" where c.name is not null"
	f" and c.archived = 0"
	f" and p.discordID = {playerID}"
	f" ORDER BY c.name ASC")
	cur.execute(sql)
	res = cur.fetchall()
	db.commit()
	if res:
		return res
	return None

@initConn
async def getCharactersOnProbation():
	sql = f'SELECT ID, name from Characters where on_probation = 1'
	cur.execute(sql)
	res = cur.fetchall()
	db.commit()
	if res:
		return res
	return None

@initConn
async def getCharactersOnArchived():
	sql = f'SELECT ID, name from Characters where archived = 1'
	cur.execute(sql)
	res = cur.fetchall()
	db.commit()
	if res:
		return res
	return None


###################################################
###				UPDATE COMMANDS					###
###################################################

@initConn
async def linkDiscordToCharacters(discordID, characterIDs):
	sql = f"UPDATE Characters set discordID={discordID} WHERE ID in ({','.join(characterIDs)})"
	cur.execute(sql)
	db.commit()
	return cur.rowcount

@initConn
async def initNewCharacter(characterIDs):
	sql = f"UPDATE Characters set on_probation=-1 WHERE ID in ({','.join(characterIDs)})"
	cur.execute(sql)
	db.commit()
	return cur.rowcount

@initConn
async def linkDiscordToPlayer(discordID, playerName):
	# First, see if this player already exists in the table
	sql = f'SELECT * from Players where discordID={int(discordID)}'
	cur.execute(sql)
	res = cur.fetchone()
	if res: # we need to update the name
		sql = f"UPDATE Players set name='{playerName}' WHERE discordID ={int(discordID)}"
		cur.execute(sql)
		db.commit()
		return ("update",cur.rowcount)
	else:
		sql = f"INSERT INTO Players (name,discordID) VALUES ('{playerName}',{int(discordID)})"
		cur.execute(sql)
		db.commit()
		return ("insert",cur.rowcount)

@initConn
async def archiveCharacterByID(playerID):
	sql = (f"UPDATE Characters SET archived = 1 WHERE ID = {playerID}")
	cur.execute(sql)
	res = cur.rowcount
	db.commit()
	if res:
		return res
	else:
		return None

@initConn
async def unarchiveCharacterByID(playerID):
	sql = (f"UPDATE Characters SET archived = 0 WHERE ID = {playerID}")
	cur.execute(sql)
	res = cur.rowcount
	db.commit()
	if res:
		return res
	else:
		return None