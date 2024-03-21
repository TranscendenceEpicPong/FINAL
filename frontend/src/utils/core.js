import { clearBlockList, clearChats, clearFriendActiveList, clearFriendWaitingList, getData, setData } from "../store.js";
import { updateFriendStatus } from "./friends.js";

function updateUsername(user)
{
	let reload = true;
	if (getData('route.path'))
		reload = !getData('route.path').startsWith(`/games/`) && !getData('route.path').startsWith(`/tournaments`);

	const userId = user.id;
	const username = user.username;
	let old_username = '';

	if (userId === getData('auth.user.id'))
		setData({auth: {user: {username}}});
	const friends = getData('friends.active');
	const updated_friends = friends.map(f => {
		if (f.sender.id === userId)
		{
			old_username = f.sender.username;
			f.sender.username = username;
		}
		else if (f.receiver.id === userId)
		{
			old_username = f.receiver.username;
			f.receiver.username = username;
		}
		return f;
	});
	clearFriendActiveList();
	setData({friends: {active: updated_friends}}, {reload});

	const friendsWaiting = getData('friends.waiting');
	const updated_friends_waiting = friendsWaiting.map(f => {
		if (f.sender.id === userId)
			f.sender.username = username;
		else if (f.receiver.id === userId)
			f.receiver.username = username;
		return f;
	});
	clearFriendWaitingList();
	setData({friends: {waiting: updated_friends_waiting}}, {reload});

	const blocks = getData('blocks');
	const updated_blocks = blocks.map(b => {
		if (b.sender.id === userId)
			b.sender.username = username;
		else if (b.receiver.id === userId)
			b.receiver.username = username;
		return b;
	});
	clearBlockList();
	setData({blocks: updated_blocks}, {reload});

	const chats = getData('chats');
	const index = chats.findIndex(chat => chat['username'] === old_username);
	if (index !== -1)
	{
		clearChats();
		const messages = chats[index];
		chats.splice(index, 1);
		for (let i = 0; i < messages.messages.length; i++)
		{
			if (messages.messages[i].sender.username === old_username)
				messages.messages[i].sender.username = username;
			else if (messages.messages[i].receiver.username === old_username)
				messages.messages[i].receiver.username = username;
		}
		chats.push({username, messages: [...messages.messages]});
		setData({chats}, {reload});
	}
}

export function analyzeCoreRequest(event)
{
    console.log(event);
	if (event.type === 'update_status')
		updateFriendStatus(event.user.username, event.status);
	else if (event.type === 'update_username')
		updateUsername(event.user);
	else
		showToast(event.content);
	// if (event.type === 'error')
	// 	return alert(event.message);
	// if (event.action === 'add')
	// {
	// 	if (!isInWaitingList(event.sender, event.receiver))
	// 		addFriendWaitingItem(event);
	// 	else
	// 		addFriendItem(event);
	// }
	// else if (event.action === 'delete')
	// {
	// 	removeFriendWaitingItem(event);
	// 	removeFriendItem(event);
	// 	if (isCurrentUser(event.sender.username))
	// 		removeUsername(event.receiver.username);
	// 	else
	// 		removeUsername(event.sender.username);
	// }
	// else if (event.action === 'accept')
	// {
	// 	addFriendItem(event);
	// }
}