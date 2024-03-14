import { loadPage } from "../router.js";
import { getData, setData, clearChats } from "../store.js";
import { isCurrentUser } from "./profile.js";
import { sendToSocket } from "./socket.js";

export async function analyzeChatRequest(event)
{
	if (event.type === 'error')
		return showToast(event.message);
	else if (event.content === '[start-game]')
		return loadPage('/games/multiplayer');
	addMessage(event);
}

/**
 * 
 * @param { string } username 
 * @param { add | accept | delete } action
 */
export function makeRequestChat(username, action)
{
	sendToSocket({action, username}, 'chats');

}

export function sendMessage(message, username)
{
	sendToSocket({
		type: "chat",
		message: message,
		username: username,
	}, 'chats');
}

export function addMessage(message, reload = true)
{
	const username = isCurrentUser(message.sender.username) ? message.receiver.username : message.sender.username;
	const chats = getData('chats');
	clearChats();
	const index = chats.findIndex(chat => chat['username'] === username);
	if (index === -1)
	{
		chats.push({username, messages: [message]});
		if (getData('route.path'))
			setData({chats}, {reload: !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`)});
		else
			setData({chats});
		return;
	}
	chats[index]['messages'].push(message);
	if (getData('route.path'))
		setData({chats}, {reload: !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`)});
	else
		setData({chats});
}

export function removeUsername(username)
{
	const chats = getData('chats');
	const index = chats.findIndex(chat => chat['username'] === username);
	if (index === -1)
		return;
	chats.splice(index, 1);
	clearChats();
	setData({chats}, {reload: !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`)});
	if (getData('route.path') === `/chats/${username}`)
		loadPage('/');
}

export function getMessagesWith(username)
{
	const chats = getData('chats');
	const index = chats.findIndex(chat => chat['username'] === username);
	if (index === -1)
		return [];
	return chats[index]['messages'];
}
