const getBlocks = () => JSON.parse(localStorage.getItem('blocks'));

function setBlocks(blocks)
{
	for (const block of blocks)
		appendBlock(block.username);
}

function appendBlock(block)
{
	const tr = document.createElement('tr');
	tr.id = `block-active-${block}`;
	const tds = {
		username: document.createElement('td'),
		remove: document.createElement('td'),
	};
	const buttons = {
		remove: createButton("Supprimer", [{name: "class", value: "btn btn-danger"}, {name: "data-bs-block", value: block}]),
	};
	tds.username.innerText = block;
	tds.remove.appendChild(buttons.remove)
	buttons.remove.addEventListener('click', () => removeBlock(block));
	for (const td in tds)
		tr.appendChild(tds[td]);
	document.getElementById('tbody-blocks-active').appendChild(tr);
}

function removeBlockFromActiveList(username)
{
	const block = document.querySelector(`#block-active-${username}`);
	block && block.remove();
}

async function loadBlocksFromApi()
{
	await fetch('/api/blocks')
	.then(async (response) => {
		setBlocks(await response.json());
	})
}

function analyzeBlocking(data)
{
	data = JSON.parse(data.data);
	if (data.type === 'error')
		return alert(data.message);
	if (data.action === 'add')
	{
		console.log(getUsername(), data.sender, getUsername() === data.sender);
		if (getUsername() === data.sender)
		{
			appendBlock(data.receiver);
			removeFriendFromActiveList(data.receiver);
			removeFriendFromWaitlist(data.receiver);
		}
		else
		{
			removeFriendFromActiveList(data.sender);
			removeFriendFromWaitlist(data.sender);
		}
	}
	else if (data.action === 'delete' && getUsername() === data.sender)
		removeBlockFromActiveList(data.receiver);
}

function addBlock(username)
{
	getSocket('blocks').send(JSON.stringify({
		'type': 'blocks',
		'username': username,
		'action': 'add'
	}));
}

async function acceptRequestBlock(username)
{
	getSocket('blocks').send(JSON.stringify({
		'type': 'blocks',
		'username': username,
		'action': 'accept'
	}));
}

async function removeBlock(username)
{
	getSocket('blocks').send(JSON.stringify({
		'type': 'blocks',
		'username': username,
		'action': 'delete'
	}));
}

function makeAction(data)
{
	console.log(data);
	if (data.action === 'block')
		blockBlockToWaitlist(data.sender, data.sender)
}

document.addEventListener('DOMContentLoaded', async () => {
	const form_block_block = document.getElementById('form-add-block');
	form_block_block && form_block_block.addEventListener('submit', async (e) => {
		e.preventDefault();
		addBlock(e.target.username.value);
		form_block_block.reset();
	});

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

	if (getCookie('authorization'))
	{
		await loadBlocksFromApi();
	}
});
