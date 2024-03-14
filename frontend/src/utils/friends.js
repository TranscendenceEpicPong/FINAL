import { getData, setData, store, clearFriendWaitingList, clearFriendActiveList } from "../store.js";
import { removeUsername } from "./chats.js";
import { isCurrentUser } from "./profile.js";
import { sendToSocket } from "./socket.js";

export async function analyzeFriendRequest(event)
{
	if (event.type === 'error')
		return showToast(event.message);
	if (event.action === 'add')
	{
		if (!isInWaitingList(event.sender, event.receiver))
			addFriendWaitingItem(event);
		else
			addFriendItem(event);
	}
	else if (event.action === 'delete')
	{
		removeFriendWaitingItem(event);
		removeFriendItem(event);
		if (isCurrentUser(event.sender.username))
			removeUsername(event.receiver.username);
		else
			removeUsername(event.sender.username);
	}
	else if (event.action === 'accept')
	{
		addFriendItem(event);
	}
}

export function updateFriendStatus(username, status)
{
	const friends = getData('friends.active');
	const updated_friends = friends.map(f => {
		if (isCurrentUser(f.sender.username))
		{
			if (f.receiver.username === username)
				f.receiver.status = status;
		}
		else
		{
			if (f.sender.username === username)
				f.sender.status = status;
		}
		return f;
	});
	clearFriendActiveList();
	setData({friends: {active: updated_friends}}, {reload: !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`)});
}

function isInWaitingList(sender, receiver)
{
	const friendsWaiting = getData('friends.waiting');
	return friendsWaiting.some(f => {		
		if (isCurrentUser(f.sender.username) && isCurrentUser(sender.username))
		{
			if (f.receiver.username === receiver.username)
				return true;
		}
		if (isCurrentUser(f.receiver.username) && isCurrentUser(receiver.username))
		{
			if (f.sender.username === sender.username)
				return true;
		}
		if (isCurrentUser(f.sender.username) && isCurrentUser(receiver.username))
		{
			if (f.receiver.username === sender.username)
				return true;
		}
		if (isCurrentUser(f.receiver.username) && isCurrentUser(sender.username))
		{
			if (f.sender.username === receiver.username)
				return true;
		}
		return false;
	});
}

/**
 * 
 * @param { string } username 
 * @param { add | accept | delete } action 
 */
export function makeRequestFriend(username, action)
{
	sendToSocket({action, username}, 'friends');

}

export function addFriendWaitingItem(friend)
{
	setData({friends: {waiting: [{sender: friend.sender, receiver: friend.receiver}]}}, {reload: !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`)});
}

export function removeFriendWaitingItem(friend)
{
	let friends = getData('friends.waiting');
	clearFriendWaitingList();
	friends = friends.filter(f => {
		if (isCurrentUser(f.sender.username) && isCurrentUser(friend.sender.username))
		{
			if (f.receiver.username === friend.receiver.username)
				return false;
		}
		if (isCurrentUser(f.receiver.username) && isCurrentUser(friend.receiver.username))
		{
			if (f.sender.username === friend.sender.username)
				return false;
		}
		if (isCurrentUser(f.sender.username) && isCurrentUser(friend.receiver.username))
		{
			if (f.receiver.username === friend.sender.username)
				return false;
		}
		if (isCurrentUser(f.receiver.username) && isCurrentUser(friend.sender.username))
		{
			if (f.sender.username === friend.receiver.username)
				return false;
		}
		return true;
	})
	setData({friends: {waiting: friends}}, {reload: !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`)});
}

export function addFriendItem(friend)
{
	removeFriendWaitingItem(friend);
	setData({friends: {active: [{sender: friend.sender, receiver: friend.receiver}]}}, {reload: !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`)});
}

export function removeFriendItem(friend)
{
	let friends = getData('friends.active');
	clearFriendActiveList();
	friends = friends.filter(f => {
		if (isCurrentUser(f.sender.username) && isCurrentUser(friend.sender.username))
		{
			if (f.receiver.username === friend.receiver.username)
				return false;
		}
		if (isCurrentUser(f.receiver.username) && isCurrentUser(friend.receiver.username))
		{
			if (f.sender.username === friend.sender.username)
				return false;
		}
		if (isCurrentUser(f.sender.username) && isCurrentUser(friend.receiver.username))
		{
			if (f.receiver.username === friend.sender.username)
				return false;
		}
		if (isCurrentUser(f.receiver.username) && isCurrentUser(friend.sender.username))
		{
			if (f.sender.username === friend.receiver.username)
				return false;
		}
		return true;
	})
	setData({friends: {active: friends}}, {reload: !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`)});
}
