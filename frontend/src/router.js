import {getData, setData} from "./store.js";

const resourceRoutes = {
    tournaments: {
        param: 'id'
    },
    profile: {
        param: 'username'
    },
    chats: {
        param: 'username'
    },
}

export async function loadPage(link = null, pushHistory = true) {
    const router = document.querySelector('#router');
    if (link) {
        await setData({
            route: {path: link}
        }, {
            reload: false
        });
    } else {
        link = getData("route.path") ?? "/"
    }

    const split_path = link.split('/').filter(
        (segment) => !!segment.length
    )
    const params = {}
    const maybe_resource = split_path[0]
    let jsPath = link
    if (!!resourceRoutes[maybe_resource] &&
        !!resourceRoutes[maybe_resource].param &&
        split_path.length > 1
    ) {
        const param_name = resourceRoutes[maybe_resource].param
        const param_value = split_path[1]
        jsPath = `/${split_path[0]}/_${param_name}`
        params[param_name] = param_value
    }

    let page_module;
    try {
        page_module = await import(`./pages${jsPath === '/' ? '/home' : jsPath}.js`);
        if (pushHistory) {
            history.pushState({path: link}, '', link);
        }
    } catch (e)
    {
        page_module = await import(`./pages/404.js`);
    }
    const { default: page } = page_module;
    const page_component = await page(params)
    router.innerHTML = "";
    router.append(page_component.content.cloneNode(true))
    return page_component.content
}