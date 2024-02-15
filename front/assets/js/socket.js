document.addEventListener('DOMContentLoaded', () => {
	const authorization = getCookie('authorization');
	if (authorization)
		initializeSocket();
})

const prefix = `ws://${window.location.host}:8000/ws`;
const urls = {
	'friends': {
		link: 'friends',
		callback: (e) => {showRequestFriend(e);}
	},
	'blocks': {
		link: 'blocks',
		callback: (e) => {analyzeBlocking(e);}
	},
	// 'chats': {
	// 	link: 'chats',
	// 	callback: (e) => {console.log(e);}
	// },
	// 'game': {
	// 	link: 'game',
	// 	callback: (e) => {
	// 		const data = JSON.parse(e.data);
	// 		if (data.type === 'game_status')
	// 		{
	// 			if (data.status === Status.WAITING)
	// 				alert(`${data.message}`);
	// 			else if (data.status === Status.STARTED)
	// 			{}
	// 			else if (data.status === Status.ENDED)
	// 				endGame();
	// 		}
	// 		// animate(data.position.x, data.position.y);
	// 	}
	// },
}

function getSocketURL(name)
{
	return `${prefix}/${name}/?${getCookie('authorization')}`
}

const chatsSockets = {}
function initializeSocket()
{
	for (const socket in urls)
		if (urls[socket].link && !chatsSockets[socket])
			chatsSockets[socket] = createSocket(getSocketURL(urls[socket].link), urls[socket].callback);
}

function createSocket(name, callback)
{
	const socket = new WebSocket(name);
	socket.onmessage = function(e){
		callback(e);
	}
	return socket;
}

function getSocket(name)
{
	return chatsSockets[name];
}

function sendToSocket(datas, socket_name)
{
	getSocket(socket_name).send(JSON.stringify(datas));
}