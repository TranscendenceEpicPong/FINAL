
import { getCookie } from "../api.js";
import { analyzeBlockRequest } from "./blocks.js";
import { analyzeChatRequest } from "./chats.js";
import { analyzeFriendRequest } from "./friends.js";
import { analyzeGameRequest } from "./game.js";
import { analyzeCoreRequest } from "./core.js";

const prefix = `${process.env.BASE_WS}`;

const urls = {
    'friends': {
        link: 'friends',
        auto_initialize: true,
        callback: (e) => {
            console.log(e.data);
            analyzeFriendRequest(JSON.parse(e.data));
        }
    },
    'blocks': {
        link: 'blocks',
        auto_initialize: true,
        callback: (e) => {
            console.log(e.data);
            analyzeBlockRequest(JSON.parse(e.data));
        }
    },
    'chats': {
        link: 'chats',
        auto_initialize: true,
        callback: (e) => {
            console.log(e.data);
            analyzeChatRequest(JSON.parse(e.data));
        }
    },
    'game': {
        link: 'game',
        auto_initialize: true,
        callback: (e) => {
            analyzeGameRequest(JSON.parse(e.data));
        }
    },
    'core': {
        link: 'core',
        auto_initialize: true,
        callback: (e) => {
            analyzeCoreRequest(JSON.parse(e.data));
        }
    },
}

const chatsSockets = {};

function getSocketURL(name)
{
    console.log(prefix)
	return `${prefix}/${name}/?${getCookie('authorization')}`
}

export function initializeSockets()
{
    console.info("Initialize sockets");
    for (const socket in urls)
        if (urls[socket].auto_initialize)
            initializeSocket(socket);
}

export function initializeSocket(name)
{
    if (urls[name].link && !chatsSockets[name])
    {
        console.log(getSocketURL(urls[name].link));
        chatsSockets[name] = createSocket(getSocketURL(urls[name].link), urls[name].callback);
    }

}

export function resetSockets()
{
    for (const socket in urls)
    {
        console.log(`SOCKET NAME : ${urls[socket].link}`);
        console.log(chatsSockets[socket]);
        resetSocket(socket);
        console.log(chatsSockets[socket]);
    }
}

export function resetSocket(name)
{
    if (urls[name].link && chatsSockets[name])
    {
        chatsSockets[name].close();
        chatsSockets[name] = undefined;
    }
}

export function createSocket(name, callback)
{
	const socket = new WebSocket(name);
	socket.onmessage = function(e){
		callback(e);
	}
    socket.onopen = () => {
        console.log(`Socket "${name}" connected`);
    }
    socket.onclose = () => {
        console.log(`Socket "${name}" disconnected`);
    }
	return socket;
}

export function getSocket(name)
{
	return chatsSockets[name];
}

export function sendToSocket(datas, socket_name)
{
    if (!getSocket(socket_name) || getSocket(socket_name).readyState !== WebSocket.OPEN)
    {
        console.log('Socket not ready');
        return;
    }
	getSocket(socket_name).send(JSON.stringify(datas));
}