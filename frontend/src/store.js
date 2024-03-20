import {loadPage} from "./router.js";
import {isArray, isObject} from "./utils.js";

const store = {};

const schema = {
    route: {
        path: 'string',
        params: 'object'
    },
    auth: {
        loggedIn: 'boolean',
        user: {
            id: 'number',
            email: 'string',
            username: 'string',
            status: 'string',
            avatar: 'string',
            a2f_enabled: 'boolean',
            a2f_verified: 'boolean'
        },
        expiresAt: 'number',
    },
    auth_42: {
        code: 'string',
    },
    mode: {
        online: 'boolean'
    },
    game: {
        waiting: 'boolean',
        mode: ['local', 'duel', 'tournament'],
        tournament: {
            players: 'array'
        },
        current: {
            id: 'string',
            mode: 'string',
            players: 'array',
            status: 'string',
            winner: 'string'
        }
    },
    serverInfo: {
        hostname: 'string',
        version: 'number',
        available: 'boolean'
    },
    displayProfileMenu: "string",
    friends: {
        active: "array",
        waiting: "array",
    },
    blocks: "array",
	chats: "array"
};

const isValid = (prop, value, schema_prop) => {
    const value_type = typeof value;
    if (schema_prop === "array" && isArray(value)) return true;
    if (schema_prop === "object" && isObject(value)) return true;
    if (isArray(schema_prop)) return schema_prop.includes(value);
    return value_type === schema_prop;
};

export const clearFriendWaitingList = () => {
    store.friends.waiting = [];
}

export const clearFriendActiveList = () => {
    store.friends.active = [];
}

export const clearBlockList = () => {
    store.blocks = [];
}

export const clearChats = () => {
	store.chats = [];
}

export function clearStore()
{
    Object.keys(store).forEach(key => delete store[key]);
}

export async function resetStore()
{
    clearStore();
    await initStore();
}

export const setData = async (
    update,
    options = { reload: true },
    store_iter = store,
    schema_iter = schema
) => {
    if (typeof update !== "object") {
        console.error("Cannot update state with value: ", update);
    }

    for (const prop in update) {
        // console.info(prop)
        if (!prop in schema_iter) {
            return console.error(
                `${prop} in not a valid key for `,
                schema_iter
            );
        }
        if (typeof update[prop] === "object" &&
            update[prop] !== null &&
            schema_iter[prop] !== "array" &&
            schema_iter[prop] !== "object"
        ) {
            if (!store_iter[prop]) {
                // console.warn(`Init prop ${prop} at {}`)
                store_iter[prop] = {};
            }
            await setData(
                update[prop],
                Object.assign({}, options, {reload: false}),
                store_iter[prop],
                schema_iter[prop]
            );
        }
        else if (update[prop] === null) {
            store_iter[prop] = undefined;
        }
        else if (isValid(prop, update[prop], schema_iter[prop])) {
            if (schema_iter[prop] === "array") {
                if (!store_iter[prop]) store_iter[prop] = [];
                // console.warn(prop, schema_iter[prop], store_iter[prop], update[prop])
                store_iter[prop].push(...update[prop]);
            } else {
                store_iter[prop] = update[prop];
            }
        }
        else {
            console.log(schema_iter);
            console.log(update);
            console.error(
                `Error '${prop}': Expected type ${typeof schema_iter[prop]}, got ${typeof update[
                    prop
                ]}`
            );
        }
    }

    if (options.reload === true) {
        console.info(`Loading page ${store.route.path}`)
        await loadPage(store.route?.path ?? '/', false);
    }

    if (!window.store) window.store = {};
    Object.assign(window.store, store);
};

async function fetchServerInfo()
{
    const serverInfoUrl = `${process.env.BASE_URL}/server_info/`
    const serverInfo = await fetch(serverInfoUrl, {
        credentials: "include",
        mode: "cors",
    })
    console.log(serverInfo);
    return serverInfo.json()
}

export async function initStore() {
    const server_info = await fetchServerInfo()
    setData({
        serverInfo: server_info,
        game: {
            waiting: false
        }
    }, {
        reload: false
    })
}

export const getData = (path) => {
    const keys = path.split(".");

    let current = store;
    let schema_iter = schema;
    keys.forEach((k) => {
        if (typeof current[k] === "undefined") {
            if (typeof schema_iter[k] === "undefined") {
                console.error(`Didn't find ${k} in `, current);
                return undefined;
            }

            if (isObject(schema_iter[k])) current[k] = {};
            else if (schema_iter[k] === "array") current[k] = [];
        }
        current = current[k];
        schema_iter = schema_iter[k];
    });
    return current;
};

export function getSchema()
{
    return schema;
}