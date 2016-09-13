""" Contains functions used to write specific server packets to byte streams """
from helpers import packetHelper
from constants import dataTypes
from helpers import userHelper
from objects import glob
from constants import userRanks
from constants import packetIDs
from constants import privileges

""" Login errors packets """
def loginFailed():
	return packetHelper.buildPacket(packetIDs.server_userID, [[-1, dataTypes.SINT32]])

def forceUpdate():
	return packetHelper.buildPacket(packetIDs.server_userID, [[-2, dataTypes.SINT32]])

def loginBanned():
	packets = packetHelper.buildPacket(packetIDs.server_userID, [[-1, dataTypes.SINT32]])
	packets += notification("You are banned. You can appeal after one month since your ban by sending an email to support@ripple.moe> from the email address you've used to sign up.")
	return packets

def loginLocked():
	packets = packetHelper.buildPacket(packetIDs.server_userID, [[-1, dataTypes.SINT32]])
	packets += notification("Your account is locked. You can't log in, but your profile and scores are still visible from the website. If you want to unlock your account, send an email to support@ripple.moe from the email address you've used to sign up.")
	return packets

def loginError():
	return packetHelper.buildPacket(packetIDs.server_userID, [[-5, dataTypes.SINT32]])

def needSupporter():
	return packetHelper.buildPacket(packetIDs.server_userID, [[-6, dataTypes.SINT32]])

def needVerification():
	return packetHelper.buildPacket(packetIDs.server_userID, [[-8, dataTypes.SINT32]])


""" Login packets """
def userID(uid):
	return packetHelper.buildPacket(packetIDs.server_userID, [[uid, dataTypes.SINT32]])

def silenceEndTime(seconds):
	return packetHelper.buildPacket(packetIDs.server_silenceEnd, [[seconds, dataTypes.UINT32]])

def protocolVersion(version = 19):
	return packetHelper.buildPacket(packetIDs.server_protocolVersion, [[version, dataTypes.UINT32]])

def mainMenuIcon(icon):
	return packetHelper.buildPacket(packetIDs.server_mainMenuIcon, [[icon, dataTypes.STRING]])

def userSupporterGMT(supporter, GMT):
	result = 1
	if supporter:
		result += 4
	if GMT:
		result += 2
	return packetHelper.buildPacket(packetIDs.server_supporterGMT, [[result, dataTypes.UINT32]])

def friendList(userID):
	friends = userHelper.getFriendList(userID)
	return packetHelper.buildPacket(packetIDs.server_friendsList, [[friends, dataTypes.INT_LIST]])

def onlineUsers():
	userIDs = []
	users = glob.tokens.tokens

	# Create list with all connected (and not restricted) users
	for _, value in users.items():
		if not value.restricted:
			userIDs.append(value.userID)

	return packetHelper.buildPacket(packetIDs.server_userPresenceBundle, [[userIDs, dataTypes.INT_LIST]])


""" Users packets """
def userLogout(userID):
	return packetHelper.buildPacket(packetIDs.server_userLogout, [[userID, dataTypes.SINT32], [0, dataTypes.BYTE]])

def userPanel(userID, force = False):
	# Connected and restricted check
	userToken = glob.tokens.getTokenFromUserID(userID)
	if userToken is None:
		return bytes()
	if userToken.restricted == True and force == False:
		return bytes()

	# Get user data
	username = userToken.username
	timezone = 24+userToken.timeOffset
	country = userToken.country
	gameRank = userToken.gameRank
	latitude = userToken.getLatitude()
	longitude = userToken.getLongitude()

	# Get username color according to rank
	# Only admins and normal users are currently supported
	if username == "FokaBot":
		userRank = userRanks.MOD
	elif userHelper.isInPrivilegeGroup(userID, "community manager"):
		userRank = userRanks.MOD
	elif userHelper.isInPrivilegeGroup(userID, "developer"):
		userRank = userRanks.ADMIN
	elif (userToken.privileges & privileges.USER_DONOR) > 0:
		userRank = userRanks.SUPPORTER
	else:
		userRank = userRanks.NORMAL

	return packetHelper.buildPacket(packetIDs.server_userPanel,
	[
		[userID, dataTypes.SINT32],
		[username, dataTypes.STRING],
		[timezone, dataTypes.BYTE],
		[country, dataTypes.BYTE],
		[userRank, dataTypes.BYTE],
		[longitude, dataTypes.FFLOAT],
		[latitude, dataTypes.FFLOAT],
		[gameRank, dataTypes.UINT32]
	])


def userStats(userID, force = False):
	# Get userID's token from tokens list
	userToken = glob.tokens.getTokenFromUserID(userID)

	if userToken is None:
		return bytes()
	if (userToken.restricted == True or userToken.irc == True) and force == False:
		return bytes()

	return packetHelper.buildPacket(packetIDs.server_userStats,
	[
		[userID, dataTypes.UINT32],
		[userToken.actionID, dataTypes.BYTE],
		[userToken.actionText, dataTypes.STRING],
		[userToken.actionMd5, dataTypes.STRING],
		[userToken.actionMods, dataTypes.SINT32],
		[userToken.gameMode, dataTypes.BYTE],
		[userToken.beatmapID, dataTypes.SINT32],
		[userToken.rankedScore, dataTypes.UINT64],
		[userToken.accuracy, dataTypes.FFLOAT],
		[userToken.playcount, dataTypes.UINT32],
		[userToken.totalScore, dataTypes.UINT64],
		[userToken.gameRank, dataTypes.UINT32],
		[userToken.pp if userToken.pp <= 65535 else 0, dataTypes.UINT16]
	])


""" Chat packets """
def sendMessage(fro, to, message):
	return packetHelper.buildPacket(packetIDs.server_sendMessage, [
		[fro, dataTypes.STRING],
		[message, dataTypes.STRING],
		[to, dataTypes.STRING],
		[userHelper.getID(fro), dataTypes.SINT32]
	])

def channelJoinSuccess(userID, chan):
	return packetHelper.buildPacket(packetIDs.server_channelJoinSuccess, [[chan, dataTypes.STRING]])

def channelInfo(chan):
	channel = glob.channels.channels[chan]
	return packetHelper.buildPacket(packetIDs.server_channelInfo, [
		[chan, dataTypes.STRING],
		[channel.description, dataTypes.STRING],
		[channel.getConnectedUsersCount(), dataTypes.UINT16]
	])

def channelInfoEnd():
	return packetHelper.buildPacket(packetIDs.server_channelInfoEnd, [[0, dataTypes.UINT32]])

def channelKicked(chan):
	return packetHelper.buildPacket(packetIDs.server_channelKicked, [[chan, dataTypes.STRING]])

def userSilenced(userID):
	return packetHelper.buildPacket(packetIDs.server_userSilenced, [[userID, dataTypes.UINT32]])


""" Spectator packets """
def addSpectator(userID):
	return packetHelper.buildPacket(packetIDs.server_spectatorJoined, [[userID, dataTypes.SINT32]])

def removeSpectator(userID):
	return packetHelper.buildPacket(packetIDs.server_spectatorLeft, [[userID, dataTypes.SINT32]])

def spectatorFrames(data):
	return packetHelper.buildPacket(packetIDs.server_spectateFrames, [[data, dataTypes.BBYTES]])

def noSongSpectator(userID):
	return packetHelper.buildPacket(packetIDs.server_spectatorCantSpectate, [[userID, dataTypes.SINT32]])

def fellowSpectatorJoined(userID):
	return packetHelper.buildPacket(packetIDs.server_fellowSpectatorJoined, [[userID, dataTypes.SINT32]])

def fellowSpectatorLeft(userID):
	return packetHelper.buildPacket(packetIDs.server_fellowSpectatorLeft, [[userID, dataTypes.SINT32]])


""" Multiplayer Packets """
def createMatch(matchID):
	# Make sure the match exists
	if matchID not in glob.matches.matches:
		return None

	# Get match binary data and build packet
	match = glob.matches.matches[matchID]
	return packetHelper.buildPacket(packetIDs.server_newMatch, match.getMatchData())

def updateMatch(matchID):
	# Make sure the match exists
	if matchID not in glob.matches.matches:
		return None

	# Get match binary data and build packet
	match = glob.matches.matches[matchID]
	return packetHelper.buildPacket(packetIDs.server_updateMatch, match.getMatchData())

def matchStart(matchID):
	# Make sure the match exists
	if matchID not in glob.matches.matches:
		return None

	# Get match binary data and build packet
	match = glob.matches.matches[matchID]
	return packetHelper.buildPacket(packetIDs.server_matchStart, match.getMatchData())

def disposeMatch(matchID):
	return packetHelper.buildPacket(packetIDs.server_disposeMatch, [[matchID, dataTypes.UINT32]])

def matchJoinSuccess(matchID):
	# Make sure the match exists
	if matchID not in glob.matches.matches:
		return None

	# Get match binary data and build packet
	match = glob.matches.matches[matchID]
	data = packetHelper.buildPacket(packetIDs.server_matchJoinSuccess, match.getMatchData())
	return data

def matchJoinFail():
	return packetHelper.buildPacket(packetIDs.server_matchJoinFail)

def changeMatchPassword(newPassword):
	return packetHelper.buildPacket(packetIDs.server_matchChangePassword, [[newPassword, dataTypes.STRING]])

def allPlayersLoaded():
	return packetHelper.buildPacket(packetIDs.server_matchAllPlayersLoaded)

def playerSkipped(userID):
	return packetHelper.buildPacket(packetIDs.server_matchPlayerSkipped, [[userID, dataTypes.SINT32]])

def allPlayersSkipped():
	return packetHelper.buildPacket(packetIDs.server_matchSkip)

def matchFrames(slotID, data):
	return packetHelper.buildPacket(packetIDs.server_matchScoreUpdate, [[data[7:11], dataTypes.BBYTES], [slotID, dataTypes.BYTE], [data[12:], dataTypes.BBYTES]])

def matchComplete():
	return packetHelper.buildPacket(packetIDs.server_matchComplete)

def playerFailed(slotID):
	return packetHelper.buildPacket(packetIDs.server_matchPlayerFailed, [[slotID, dataTypes.UINT32]])

def matchTransferHost():
	return packetHelper.buildPacket(packetIDs.server_matchTransferHost)


""" Other packets """
def notification(message):
	return packetHelper.buildPacket(packetIDs.server_notification, [[message, dataTypes.STRING]])

def banchoRestart(msUntilReconnection):
	return packetHelper.buildPacket(packetIDs.server_restart, [[msUntilReconnection, dataTypes.UINT32]])