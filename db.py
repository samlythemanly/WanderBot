'''
Database Query Engine
	Handles all DB interactions.
'''
import mysql.connector
from private_info import DB_HOST, DB_USER, DB_PASSWORD, DB_CATALOG

db = mysql.connector.connect(
	host=DB_HOST,
	user=DB_USER,
	passwd=DB_PASSWORD,
	database=DB_CATALOG
	)

cur = db.cursor(dictionary=True)


async def getCharacterFromID(charID):
	sql = f'SELECT * from Characters where ID={int(charID)}'
	cur.execute(sql)
	res = cur.fetchone()
	if res:
		return res
	return None

async def linkDiscordToCharacters(discordID, characterIDs):
	sql = f"UPDATE Characters set discordID={discordID} WHERE ID in ({','.join(characterIDs)})"
	cur.execute(sql)
	db.commit()
	return cur.rowcount

async def getCharactersFromIDs(charIDs):
	sql = f"SELECT name FROM Characters WHERE ID in ({','.join(charIDs)})"
	cur.execute(sql)
	res = cur.fetchall()
	if res:
		return [c['name'] for c in res]
	else:
		return None