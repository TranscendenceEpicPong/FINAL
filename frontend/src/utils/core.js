import { updateFriendStatus } from "./friends.js";

export function analyzeCoreRequest(event)
{
    console.log(event);
	if (event.type !== 'alert')
		updateFriendStatus(event.user.username, event.status);
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