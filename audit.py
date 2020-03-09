from importlib import reload ## DEBUGGING
import datetime
from db.db import db
import logging
import asyncio
from pprint import pprint

l = logging.info

# If a message gets deleted, we want to know who deleted it and what was the original message.
# If the message was deleted by someone other than the original author we need to look at the internal audit logs
async def logDeletedMessage(message, action_type):
	# In order to figure out if the user deleted the message themselves or if someone else did,
	#	we need to see if an event was recently inserted into the audit logs, say...a couple seconds ago.
	print(f"Message created at: {message.created_at}")
	# timediff = datetime.datetime.utcnow() - datetime.timedelta(seconds=5)
	async for entry in message.guild.audit_logs(limit=5, action=action_type):
		pprint(dir(entry))
		if (datetime.datetime.utcnow() - entry.created_at).total_seconds() < 5:
			print('found an entry')
		# for ch in message.guild.channels:
		# 	if str(ch) == const.AUDIT_CHANNEL:
		# 		return await ch.send(f"{entry.user.name} just deleted the following message from {message.author.name} in channel {message.channel}: `{message.content}`")