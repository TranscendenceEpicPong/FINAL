const getFriends = () => JSON.parse(localStorage.getItem('friends'));

function setFriends(friends)
{
	for (const friend of friends)
		addFriend(friend.username);
}

function addFriend(friend)
{
	const tr = document.createElement('tr');
	tr.id = `friend-active-${friend}`;
	const tds = {
		username: document.createElement('td'),
		block: document.createElement('td'),
		remove: document.createElement('td'),
	};
	const buttons = {
		remove: createButton("Supprimer", [{name: "class", value: "btn btn-danger"}, {name: "data-bs-friend", value: friend}]),
		block: createButton("Bloquer", [{name: "class", value: "btn btn-secondary"}, {name: "data-bs-friend", value: friend}]),
	};
	tds.username.innerText = friend;
	tds.block.appendChild(buttons.block)
	tds.remove.appendChild(buttons.remove)
	buttons.block.addEventListener('click', () => addBlock(friend));
	buttons.remove.addEventListener('click', () => removeFriend(friend));
	for (const td in tds)
		tr.appendChild(tds[td]);
	document.getElementById('tbody-friends-active').appendChild(tr);
}

function setFriendsWaiting(friends)
{
	for (const friend of friends)
		addFriendToWaitlist(friend.username, friend.sender);
}

function addFriendToWaitlist(friend, sender)
{
	const tr = document.createElement('tr');
	tr.id = `friend-waiting-${friend}`
	const tds = {
		username: document.createElement('td'),
		add: document.createElement('td'),
		remove: document.createElement('td'),
	};
	const buttons = {
		add: createButton("Ajouter", [{name: "class", value: "btn btn-primary"}, {name: "data-bs-friend", value: friend}]),
		remove: createButton("Supprimer", [{name: "class", value: "btn btn-danger"}, {name: "data-bs-friend", value: friend}]),
		cancel: createButton("Annuler", [{name: "class", value: "btn btn-secondary"}, {name: "data-bs-friend", value: friend}]),
	};
	tds.username.innerText = friend;
	if (!isCurrentUsername(sender))
		tds.add.appendChild(buttons.add)
	tds.remove.appendChild(isCurrentUsername(sender) ? buttons.cancel : buttons.remove)
	buttons.add.addEventListener('click', () => {
		acceptRequestFriend(friend);
	});
	buttons.cancel.addEventListener('click', () => {
		removeFriend(friend);
	});
	buttons.remove.addEventListener('click', () => {
		removeFriend(friend);
	});
	for (const td in tds)
		tr.appendChild(tds[td]);
	document.getElementById('tbody-friends-waiting').appendChild(tr);
}

function removeFriendFromWaitlist(username)
{
	const friend = document.querySelector(`#friend-waiting-${username}`);
	friend && friend.remove();
}

function removeFriendFromActiveList(username)
{
	const friend = document.querySelector(`#friend-active-${username}`);
	friend && friend.remove();
}

async function loadFriendsFromApi()
{
	await fetch('/api/friends')
	.then(async (response) => {
		setFriends(await response.json());
	})
}

function showRequestFriend(data)
{
	data = JSON.parse(data.data);
	if (data.type === 'error')
		return alert(data.message);
	if (data.action === 'add')
		addFriendToWaitlist(getUser().username === data.sender ? data.receiver : data.sender, data.sender);
	else if (data.action === 'accept')
	{
		removeFriendFromWaitlist(getUser().username === data.sender ? data.receiver : data.sender);
		addFriend(getUser().username === data.sender ? data.receiver : data.sender)
	}
	else if (data.action === 'delete')
	{
		removeFriendFromWaitlist(getUser().username === data.sender ? data.receiver : data.sender);
		removeFriendFromActiveList(getUser().username === data.sender ? data.receiver : data.sender);
	}
}

function sendRequestFriend(username)
{
	sendToSocket({
		'type': 'friends',
		'username': username,
		'action': 'add'
	}, 'friends');
}

async function acceptRequestFriend(username)
{
	getSocket('friends').send(JSON.stringify({
		'type': 'friends',
		'username': username,
		'action': 'accept'
	}));
}

async function removeFriend(username)
{
	getSocket('friends').send(JSON.stringify({
		'type': 'friends',
		'username': username,
		'action': 'delete'
	}));
}

async function loadFriendsWaitingFromApi()
{
	await fetch('/api/friends/waiting')
	.then(async (response) => {
		setFriendsWaiting(await response.json());
	})
}

async function loadFriendsPendingFromApi()
{
	await fetch('/api/friends/pending')
	.then(async (response) => {
		setFriendsWaiting(await response.json());
	})
}

function makeAction(data)
{
	console.log(data);
	if (data.action === 'add')
		addFriendToWaitlist(data.sender, data.sender)
}

document.addEventListener('DOMContentLoaded', async () => {
	function _getCookies()
	{
		return document.cookie.split(';');
	}

	function _getCookie(name)
	{
		for (const cookie of getCookies())
		{
			const parts = cookie.split('=');
			if (parts.length === 2 && parts[0].trim() === name)
				return parts[1].trim();
		}
		return undefined;
	}

	const form_add_friend = document.getElementById('form-add-friend');
	form_add_friend && form_add_friend.addEventListener('submit', async (e) => {
		e.preventDefault();
		sendRequestFriend(e.target.username.value);
		form_add_friend.reset();
	});

	if (getCookie('authorization'))
	{
		await loadFriendsFromApi();
		await loadFriendsWaitingFromApi();
		await loadFriendsPendingFromApi();
	}
});
