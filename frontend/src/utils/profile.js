import { getUserInfo } from "../api.js";
import { loadPage } from "../router.js";
import { setData, getData } from "../store.js";
import { isArray } from "../utils.js";
import { addMessage } from "./chats.js";
import { initializeSockets } from "./socket.js";

export async function fetchMe()
{
    const blocksUrl = `${process.env.BASE_URL}/me/`
    return await fetch(blocksUrl, {
        credentials: "include"
    })
    .then(async (response) => {
        if (!response.ok)
            return false;
        return await response.json();
    });
}

export async function fetchFriends(status = '')
{
    const friendsUrl = `${process.env.BASE_URL}/friends/${status}`
    const friends = await fetch(friendsUrl, {
        credentials: "include"
    })
    const json = await friends.json();
    if (!isArray(json))
        return [];
    return json;
}

export async function fetchBlocks()
{
    const blocksUrl = `${process.env.BASE_URL}/blocks/`
    const blocks = await fetch(blocksUrl, {
        credentials: "include"
    })
    const json = await blocks.json();
    if (!isArray(json))
        return [];
    return json;
}

export async function fetchChats()
{
    const chatsUrl = `${process.env.BASE_URL}/chats/`
    const chats = await fetch(chatsUrl, {
        credentials: "include"
    })
    const json = await chats.json();
    if (!isArray(json))
        return [];
    return json;
}

export async function initAccess(path)
{
    const me = await fetchMe();
    const user_info = getUserInfo();

    if (!me && !user_info.loggedIn)
    {
        if (![ '/auth/login', '/auth/register', '/auth/42-register' ].includes(path))
            return await loadPage('/auth/login');
    }
    else if (!me && user_info.loggedIn)
    {
        if (user_info.user.a2f_enabled && path !== '/auth/a2f')
            return await loadPage('/auth/a2f');
        return await loadPage('/auth/login');
    }
    else
        await loadProfile();
    console.log('Path', path);
    await loadPage(path);
}

export async function loadProfile(user)
{
    const friends = {
        active: await fetchFriends(),
        waiting: [
            ...await fetchFriends('waiting'),
            ...await fetchFriends('pending')
        ],
    };

    const blocks = await fetchBlocks();
	const chats = await fetchChats();

	chats.forEach(chat => {
		addMessage(chat, false);
	});

    console.warn({
        friends,
        blocks,
        auth: {
            user: user ?? await fetchMe()
        }
    })

    setData({
        friends,
        blocks,
        auth: {
            user: user ?? await fetchMe()
        }
    }, {reload: false});

    initializeSockets();
}

export function isCurrentUser(username)
{
    return getData('auth.user.username') === username;
}

export async function getProfile(username)
{
    const profile = await fetch(`${process.env.BASE_URL}/users/${username}`, {
        credentials: "include"
    })
    .then(async (response) => {
        return await response.json();
    });
    return profile;
}