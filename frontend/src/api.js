export function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function parseJwt (token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}

export function getUserInfo() {
    const jwt = getCookie('authorization')
    if (!jwt) {
        return {loggedIn: false, user: null}
    }
    const userInfo = parseJwt(jwt)
    return {
        loggedIn: true,
        user: {
            id: userInfo.id,
            email: userInfo.email,
            username: userInfo.username,
            status: 'online',
            a2f_enabled: userInfo.a2f_enabled,
            a2f_verified: userInfo.a2f_verified
        }
    }
}

export async function postData(url = "", data = {}, method = "POST") {
    const csrfToken = getCookie('csrftoken')
    // Default options are marked with *
    const response = await fetch(url, {
        method: method, // *GET, POST, PUT, DELETE, etc.
        mode: "cors", // no-cors, *cors, same-origin
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        credentials: "include", // include, *same-origin, omit
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: "follow", // manual, *follow, error
        referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        // body: JSON.stringify({...data, csrfmi}), // body data type must match "Content-Type" header
        body: JSON.stringify(data), // body data type must match "Content-Type" header
    });
    if (!response.ok) {
        console.log("Response not ok")
        throw await response.json()
    }
    console.log(response)
    try {
        return await response.json();
    } catch (e) {
        return {'status': response.status};
    }
}

export const tournaments = {
    base_url: `${process.env.BASE_URL}/tournaments`,
    fetch_options: {
        credentials: "include",
        mode: "cors",
    },
    get: async function (id) {
        const res = await fetch(`${this.base_url}/${id}/`, this.fetch_options)
        return res.json()
    },
    list: async function (id) {
        const res = await fetch(`${this.base_url}/`, this.fetch_options)
        return res.json()
    },
    create: async function ({name, participants}) {
        console.info("Create tournament", {name, participants})
        return postData(`${this.base_url}/`, {name, participants})
    },
    join: async function ({id, alias}) {
        console.info("Join tournament", id, alias);
        return postData(`${this.base_url}/${id}/register/`, {alias})
    },
    launch: async function (id) {
        return postData(`${this.base_url}/${id}/launch/`)
    }

}
