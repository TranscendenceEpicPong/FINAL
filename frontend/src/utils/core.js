import { clearBlockList, clearFriendActiveList, clearFriendWaitingList, getData, setData } from "../store.js";
import { updateFriendStatus } from "./friends.js";

function updateUsername(user)
{
	const userId = user.id;
	const username = user.username;

	if (userId === getData('auth.user.id'))
		setData({auth: {user: {username}}});
	const friends = getData('friends.active');
	const updated_friends = friends.map(f => {
		if (f.sender.id === userId)
			f.sender.username = username;
		else if (f.receiver.id === userId)
			f.receiver.username = username;
		return f;
	});
	clearFriendActiveList();
	setData({friends: {active: updated_friends}});

	const friendsWaiting = getData('friends.waiting');
	const updated_friends_waiting = friendsWaiting.map(f => {
		if (f.sender.id === userId)
			f.sender.username = username;
		else if (f.receiver.id === userId)
			f.receiver.username = username;
		return f;
	});
	clearFriendWaitingList();
	setData({friends: {waiting: updated_friends_waiting}});

	const blocks = getData('blocks');
	const updated_blocks = blocks.map(b => {
		if (b.sender.id === userId)
			b.sender.username = username;
		else if (b.receiver.id === userId)
			b.receiver.username = username;
		return b;
	});
	clearBlockList();
	setData({blocks: updated_blocks});
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