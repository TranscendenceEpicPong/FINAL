import { getData, setData, clearBlockList } from "../store.js";
import { removeUsername } from "./chats.js";
import { removeFriendItem, removeFriendWaitingItem } from "./friends.js";
import { isCurrentUser } from "./profile.js";
import { sendToSocket } from "./socket.js";

export async function analyzeBlockRequest(event)
{
	if (event.type === 'error')
		return showToast(event.message);
	if (event.action === 'add')
	{
		addBlock(event);
	}
	else if (event.action === 'delete')
	{
		removeBlockItem(event);
	}
}

/**
 * 
 * @param { string } username 
 * @param { add | accept | delete } action 
 */
export function makeRequestBlock(username, action)
{
	sendToSocket({action, username}, 'blocks');
}

export function addBlock(blocked_user)
{
	let reload = true;
	if (getData('route.path'))
		reload = !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`);
	removeFriendWaitingItem({
		sender: blocked_user.sender,
		receiver: blocked_user.receiver,
	});
	removeFriendItem({
		sender: blocked_user.sender,
		receiver: blocked_user.receiver,
	});
	if (isCurrentUser(blocked_user.sender.username))
		removeUsername(blocked_user.receiver.username);
	else
		removeUsername(blocked_user.sender.username);
	if (isCurrentUser(blocked_user.sender.username))
		setData({blocks: [{sender: blocked_user.sender, receiver: blocked_user.receiver}]}, {reload});
}

export function removeBlockItem(block)
{
	let blocks = getData('blocks');
	clearBlockList();
	blocks = blocks.filter(b => {
		if (isCurrentUser(block.sender.username) && isCurrentUser(b.sender.username))
		{
			if (b.receiver.username === block.receiver.username)
				return false;
		}
		return true;
	})
	let reload = true;
	if (getData('route.path'))
		reload = !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`);
	setData({blocks}, {reload});
}
